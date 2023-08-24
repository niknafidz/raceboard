@echo off
"C:\Program Files (x86)\WinSCP\WinSCP.exe" ^
/command ^
"open sftp://username:password@your-server-ip" ^
"put C:\path\to\local\csv\file.csv /path/to/remote/csv/file.csv" ^
"exit"
