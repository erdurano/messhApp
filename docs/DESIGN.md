# MesshApp Design Notes


## Goals Canvas

Who| Goals   |Method |path   |body   | returns
----| ----    |---    |----   |----   | ----
consumer | login | POST | /login | user credentials | token
consumer | sign-in user to the list | POST | /users| user credentials | user info
user | Update profile | UPDATE | /users/me | profile details | user profile
user | Get user list | GET | users/ | - | List of user profiles
user | Get user list | GET | users/{uname} | - | user profile (public)
user | Get friend list | GET | /friends | - | friend list
user | Post friend req | POST | /friends/{uname}| - | friend list
user | Update Friendship status | UPDATE | /friends/{uname}| - | friend list
user | Get chat ist | GET | /chats | - | list of users who chatted before|
user | Get messages in a chat| GET | /chats/{uname}/?since= last_known_message | - | List of messages (optionally from a timestamp)
user | Post message/Initialize chat| POST | /chats/{uname} | Message Body | Send message