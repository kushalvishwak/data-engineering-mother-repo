import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from api_client import ApiResponseError, Page, RetryableRequestError, iter_api_pages


class ApiClientTests(unittest.TestCase):
    def test_yields_pages_in_cursor_order(self):
        requests = []
        pages = {
            None: Page(({"id": 1},), "next"),
            "next": Page(({"id": 2},), None),
        }

        def read_page(endpoint, cursor, token, timeout):
            requests.append((endpoint, cursor, token, timeout))
            return pages[cursor]

        result = list(
            iter_api_pages(
                "https://example.invalid/orders",
                bearer_token="test-token",
                read_page=read_page,
            )
        )

        self.assertEqual([page.items[0]["id"] for page in result], [1, 2])
        self.assertEqual([request[1] for request in requests], [None, "next"])
        self.assertEqual(requests[0][2:], ("test-token", 10.0))

    def test_retries_transient_error_with_bounded_delay(self):
        attempts = 0
        delays = []

        def read_page(_endpoint, _cursor, _token, _timeout):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RetryableRequestError("busy", retry_after_seconds=2)
            return Page((), None)

        pages = list(
            iter_api_pages(
                "https://example.invalid",
                max_retries=1,
                max_backoff_seconds=3,
                read_page=read_page,
                sleep=delays.append,
                random_value=lambda: 0.5,
            )
        )

        self.assertEqual(pages, [Page((), None)])
        self.assertEqual(attempts, 2)
        self.assertEqual(delays, [2])

    def test_rejects_repeated_cursor(self):
        def read_page(_endpoint, _cursor, _token, _timeout):
            return Page((), "same")

        with self.assertRaisesRegex(ApiResponseError, "repeated"):
            list(iter_api_pages("https://example.invalid", read_page=read_page))

    def test_stops_at_configured_page_limit(self):
        def read_page(_endpoint, _cursor, _token, _timeout):
            return Page((), "next")

        with self.assertRaisesRegex(ApiResponseError, "max_pages"):
            list(
                iter_api_pages(
                    "https://example.invalid",
                    max_pages=1,
                    read_page=read_page,
                )
            )

    def test_does_not_retry_invalid_response(self):
        def read_page(_endpoint, _cursor, _token, _timeout):
            raise ApiResponseError("bad page")

        with self.assertRaisesRegex(ApiResponseError, "bad page"):
            list(iter_api_pages("https://example.invalid", read_page=read_page))

    def test_does_not_retry_before_long_server_cooldown(self):
        delays = []

        def read_page(_endpoint, _cursor, _token, _timeout):
            raise RetryableRequestError("rate limited", retry_after_seconds=10)

        with self.assertRaisesRegex(RetryableRequestError, "rate limited"):
            list(
                iter_api_pages(
                    "https://example.invalid",
                    max_retries=2,
                    max_backoff_seconds=3,
                    read_page=read_page,
                    sleep=delays.append,
                )
            )
        self.assertEqual(delays, [])


if __name__ == "__main__":
    unittest.main()
