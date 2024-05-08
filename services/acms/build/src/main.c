#include <stdio.h>
#include <stdio_ext.h>

#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <acms_banners.h>
#include <acms_message.h>
#include <acms_command_handlers.h>

#include <libpq-fe.h>

char* user_uuid = NULL;

command_handler handlers[] = {
    create_user,
    login,
    show_profile,
    logout,
    create_group,
    add_group_user,
    show_group,
    add_device,
    get_device,
    device_control,
    add_log,
    delete_log,
    show_journal,
    clear_logs
};

void setup()
{
    setvbuf(stdout, (char *)NULL, _IONBF, 0); 
    setvbuf(stderr, (char *)NULL, _IONBF, 0); 
}

void menu(acms_logger* logger, PGconn* conn)
{
    uint8_t command;    

    puts(BANNER);
    acms_show_status_message(logger);
    printf(MENU);

    scanf("%hhu", &command);
    __fpurge(stdin);
    command--;
    
    uint8_t handlers_count = sizeof(handlers)/sizeof(command_handler);
    if (command >= handlers_count) 
    {
        acms_set_status_message(logger, STATUS_INVALID_COMMAND);
        return;
    }

    handlers[command](logger, conn, &user_uuid);
}

int main(int argc, char* argv[], char* envp[])
{
    setup();
    puts(BANNER);
    puts("[*] Initialization...");

    acms_logger logger;
    acms_init_logger(&logger);

    PGconn* conn = PQconnectdb("user=acms password=acms dbname=acms host=db port=5432");

    if (!conn)
    {
        puts("[!] Can't create conn object!");
        goto error_exit;
    }

    ConnStatusType status = PQstatus(conn);
    if (status != CONNECTION_OK)
    {
        printf("[!] Can't connect to database: %s\n", PQerrorMessage(conn));
        goto error_exit;
    }

    while (1)
        menu(&logger, conn);

error_exit:
    getchar();
    return 1;
}