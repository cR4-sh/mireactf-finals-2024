#define BANNER  "\033[2J             .-----------------------------------------------------------------------------.   \n\
             |  ____                                              ###########              |                    \n\
             | / ___|  ___  ___ _   _ _ __ ___                   ##         ##             |                    \n\
             | \\___ \\ / _ \\/ __| | | | '__/ _ \\              m###*     m     *###m         |                \n\
             |  ___) |  __/ (__| |_| | | |  __/_           ##*     ..#####,,     *##       |                    \n\
             | |____/ \\___|\\___|\\__,_|_|  \\___(_)        m##    .#############,    ##m     |                \n\
             |   ____            _        _             ##    .###     #     ###,    ##    |                    \n\
             |  / ___|___  _ __ | |_ __ _(_)_ __       m#    ###     #####     ###    #m   |                    \n\
             | | |   / _ \\| '_ \\| __/ _` | | '_ \\      ##   .##       '#'      ###,   ##   |                 \n\
             | | |__| (_) | | | | || (_| | | | | |_    ##   ###   wwwww wwwww   ###   ##   |                    \n\
             |  \\____\\___/|_| |_|\\__\\__,_|_|_| |_(_)   ##   '##  w####   ####w  ##*   ##   |                \n\
             |  ____            _            _       ,#*     *###*' *     * '*####     '#, |                    \n\
             | |  _ \\ _ __ ___ | |_ ___  ___| |_      ##,   *'*###,         ,###'`'   ,##  |                   \n\
             | | |_) | '__/ _ \\| __/ _ \\/ __| __|      *##       '*#########*'       ##'   |                  \n\
             | |  __/| | | (_) | ||  __/ (__| |_ _       ##.,#m                 m#,.##     |                    \n\
             | |_|   |_|  \\___/ \\__\\___|\\___|\\__(_)       *'  *#####m     m#####*  '*      |               \n\
             |                                                    '*#######*'              |                    \n\
             '-----------------------------------------------------------------------------'                    \n\
                                                                                                                \n\
=+= Warning Regarding Access Control and Managment System (ACMS) for SCP Laboratory                         =+= \n\
=+=                                                                                                         =+= \n\
=+= This Access Control System and Managment (ACMS) is intended solely for the official use of SCP          =+= \n\
=+= laboratory personnel.                                                                                   =+= \n\
=+=                                                                                                         =+= \n\
=+= Any unauthorized use, distribution, or access to this system is strictly prohibited. Users are          =+= \n\
=+= required to adhere to strictsecurity and confidentiality measures when operating this system. Any       =+= \n\
=+= suspicious activity or detected information leakage must be promptly reported to system administrators. =+= \n\
=+=                                                                                                         =+= \n\
=+= Please be aware that violating the rules of usage may have dire consequences for the users themselves.  =+= \n\
=+= It is imperative to comply with all guidelines and regulations to ensure personal safety and security.  =+="

#define STATUS_FORMAT_MESAGE "\n[*] Last command log: %s\n" 
#define STATUS_INVALID_COMMAND "Invalid command!"
#define STATUS_SUCCESSFULLY_COMPLETED "Successfully completed!"

#define MENU "\n[*] Terminal commands list  \n\
    1. Create user                          \n\
                                            \n\
    2. Login                                \n\
    3. Show profile                         \n\
    4. Logout                               \n\
                                            \n\
    5. Create access group                  \n\
    6. Add group participant                \n\
    7. Show group                           \n\
                                            \n\
    8. Add device                           \n\
    9. Get device                           \n\
   10. Device control                       \n\
                                            \n\
   11. Add log manually                     \n\
   12. Delete log record                    \n\
   13. Show logs                            \n\
   14. Clear logs                           \n\
\n[>] "

#define DEVICES_LIST "\n[*] ACMS devices list      \n\
    1. Acess controller                            \n\
    2. Smart-card reader                           \n\
    3. Electromagnetic lock                        \n\
    4. Sensor                                      \n\
    5. Machine gun turret                          \n\
\n[>] "