# Json-Auth
A multi-program authentication system  flask api featuring hardware id locking and license expiration + more.

## API Endpoint's
- `/uptime` returns the api's uptime.
- `/api/info` TODO but should return a clients license information.
- `/api/register` registation using a key `key[key] - username[username] - password[password] - discord[discord] - hwid[hwid]`
- `/api/add` adding time to a clients license. `username[username] - program[prog] - days[days]`
- `/api/generate` generating a key a user uses to register. `program[prog] - days[days]`
- `/api/hwid` hardware id reset `program[prog] - discord[discord]`
- `/api/auth` client logging in `username[username] - password[password] - hwid[hwid] - program[prog]`

## Usage
This is a unfinished project and most likely will stay this way. The main goal for this project was to use it as a backend for a website and discord bot. If you use my code please credit me.
