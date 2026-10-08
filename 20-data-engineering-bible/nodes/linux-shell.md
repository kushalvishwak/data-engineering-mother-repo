---
id: linux-shell
title: Linux and the Shell
tier: 4
priority: should-know
sources: [obenner/hadoop.md, obenner/hive.md, obenner/sql.md, obenner/airflow.md, cookbook]
---

# Linux and the Shell

## Say it in one line
The shell is how you inspect and operate a machine you cannot attach a debugger to — navigate the filesystem, read logs, check disk and memory, and pipe small text tools together.

## Must be able to recite
- **Navigation and inspection** — `pwd`, `ls -lh`, `cd`, `ls -lt | head` for newest files, and `find /path -name '*.csv' -mtime -1` for "what landed yesterday".
- **Permissions** — `rwx` for user, group and other; `chmod 644` for a data file, `755` for a script, `chown user:group` to fix ownership, and `ls -l` to read what you actually have.
- **Processes** — `ps -ef | grep job`, `top` for live CPU and memory, `kill <pid>` to ask politely (SIGTERM), `kill -9` only when it will not exit, `nohup cmd &` to survive logout.
- **Redirection and pipes** — `>` truncates, `>>` appends, `2>&1` folds stderr into stdout, `|` streams one command's output into the next, `> /dev/null` discards.
- **Exit codes** — 0 means success and non-zero means failure; check `$?`, chain with `&&` or `||`, and start pipeline scripts with `set -euo pipefail` so a failing step actually fails the job.
- **grep** — `grep -c` counts, `-v` inverts, `-i` ignores case, `-r` recurses, `-E` takes a real regex, `-A/-B` show context around a match.
- **awk vs sed** — `awk` splits each line into fields and computes (`awk -F, '{s+=$3} END{print s}'`), `sed` does stream substitution (`sed 's/old/new/g'`); awk is for columns, sed is for patterns.
- **The counting idiom** — `cut -d, -f2 file.csv | sort | uniq -c | sort -rn | head` gives the top values of a column, and it is the one-liner worth having memorised.
- **Slicing text** — `head -n 100`, `tail -n 100`, `tail -f` to follow a live log, `wc -l` to count rows, `cut -d, -f1,3` to select columns.
- **find with xargs** — `find . -name '*.log' -mtime +7 | xargs rm` for bulk actions; use `xargs -0` with `find -print0` when paths contain spaces.
- **Disk and memory** — `df -h` for which mount is full, `du -sh * | sort -h` for what is filling it, `free -h` for memory and swap.
- **cron** — `crontab -e` edits, `crontab -l` lists, and the five fields are minute, hour, day-of-month, month, day-of-week, so `30 8 * * 1-5` means 08:30 on weekdays.
- **ssh, scp, rsync** — `ssh user@host` for a shell on port 22, key-based login instead of passwords, `scp file user@host:/path` to copy, `rsync -avz --partial` for large or resumable transfers.
- **Environment variables** — `export VAR=value` for the current shell and its children, `echo $PATH` to see where binaries are found, `~/.bashrc` for persistence, and secrets from a vault or environment rather than hard-coded.
- **tar and gzip** — `tar -czf out.tgz dir/` to create, `tar -xzf out.tgz` to extract, `gzip`/`gunzip` for single files, and `zcat`/`zgrep` to read compressed logs without unpacking them.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it. The sources carry little Linux material, so this list stays near the minimum and the recite section above carries the command surface.
- ★ What is crontab, and what does `30 8 * * 1-5` mean? — The per-user table of scheduled commands; the five fields are minute, hour, day-of-month, month and day-of-week, so this runs at 08:30 Monday to Friday.
- ★ What is SSH, which port does it use, and why is it needed? — Secure Shell, an encrypted protocol for running commands on a remote host, on port 22 by default, and the normal way to administer servers and move data between them.
- ★ Why does a distributed cluster need password-less SSH, and how do you set it up? — The master launches and talks to daemons on every worker far too often for interactive passwords, so you generate a key pair and append the public key to each host's `authorized_keys`.
- ★ Can you run shell commands from inside a database or Hive shell? — Yes, prefix with `!` — for example `!pwd` at the Hive prompt lists the working directory; it is handy for checking a file before loading it.
- How do machines in a cluster talk to each other, and how do you verify it from the shell? — SSH launches the remote daemons and an RPC protocol carries the ongoing heartbeats and task traffic; check it with `ping`, `ssh host`, `ss -tlnp` for listeners and `nc -zv host port` for reachability.
- How do you start, stop or restart a service on Linux? — `systemctl start|stop|restart|status <service>` on any modern distribution, with `journalctl -u <service>` for its logs; the older init-script style is `service <name> start`.
- What is a daemon, and where do its scripts live? — A background service process, the Unix equivalent of a Windows service; legacy init scripts live in `/etc/init.d` and modern units live under `/etc/systemd/system`.
- Which operating system do you run data infrastructure on, and could you use Windows? — Linux, in practice RHEL/Rocky or Ubuntu; Hadoop and most data tooling can be made to run on Windows but it is not supported in earnest and nobody deploys it that way.
- ★ What is a Unix timestamp, and how do you convert it to a readable datetime? — Seconds since 1970-01-01 UTC, stored as an integer; convert with `date -d @1700000000` in the shell, `FROM_UNIXTIME()` in MySQL or Hive, and back with `UNIX_TIMESTAMP()`.
- What is an exit code, and why does your orchestrator care? — The number a process returns on exit, 0 for success; Airflow, cron wrappers and shell chains decide success, retry or alert purely from it, so a script that swallows errors and exits 0 will look like a green run.
- What is `fsck` and when do you run it? — A filesystem consistency check, run on an unmounted filesystem after a crash; the HDFS equivalent, `hdfs fsck /`, reports missing, corrupt and under-replicated blocks — see [[hadoop-hdfs]].
- You get "connection refused" running a cluster command — how do you debug it? — Confirm the daemon is actually up (`systemctl status`, `jps`), that it is listening on the expected port (`ss -tlnp`), that the hostname resolves, and that no firewall sits in between; refused means nothing is accepting on that port.
- How would you count how many times an error appears in a log, broken down by hour? — `grep ERROR app.log | awk '{print $2}' | cut -d: -f1 | sort | uniq -c`, adding `zgrep` for rotated `.gz` files. *(not in sources, but standard)*
- The disk filled up at 3 a.m. and the job failed — what do you do? — `df -h` to find the full mount, `du -sh * | sort -h` walking down to the culprit directory, `find /path -size +1G` for the big files, then rotate or archive rather than deleting blindly. *(not in sources, but standard)*
- Your script fails with "permission denied" — what do you check? — Whether the file has the execute bit (`chmod +x`), whether you own it or are in its group (`ls -l`), whether the interpreter line is right, and whether the target directory is writable by the user cron or the scheduler runs as. *(not in sources, but standard)*

## Traps
- `rm -rf` with a variable or a glob in it. Echo or `ls` the expansion first, because there is no undo and no recycle bin on a server.
- Parsing CSVs with `cut` or `awk -F,` when fields are quoted and contain commas — it silently shifts columns; use a real parser for anything you will trust.
- Assuming cron inherits your environment. Cron runs with a minimal `PATH` and no shell profile, so use absolute paths, activate the virtualenv explicitly, and redirect output to a log file.
- Reaching for `kill -9` first. It denies the process any chance to flush and clean up, which can leave a half-written file or a stale lock; send SIGTERM and wait.
- Deleting a large file that a process still holds open. `df` will not free the space until the file descriptor closes, so truncate the file or restart the writer.
- `cat file | grep x | wc -l` when `grep -c x file` does it — interviewers read the pipeline as a proxy for whether you actually work in the shell.

## Graph
- **Needs first:** —
- **Leads to:** [[containers-kubernetes]]
- **Asked together with:** [[python-for-data]]
