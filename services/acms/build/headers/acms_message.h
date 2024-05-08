#ifndef __ACMS_MESSAGE__
#define __ACMS_MESSAGE__

#include <stdint.h>

#define ACMS_LOG_SIZE       256

typedef struct _log_entry
{
    void* next;
    uint32_t ts;
    size_t msg_size;
    char* msg;
} log_entry;

typedef struct _journal_entry
{
    void* next;
    char* user_uuid;
    void* log_head;
} journal_entry;

typedef struct _logger
{
    uint8_t shown;
    char msg[ACMS_LOG_SIZE];
    void* journal_head;
} acms_logger;

void acms_init_logger(acms_logger* logger);
void acms_show_status_message(acms_logger* logger);
void acms_set_status_message_and_copy_journal(acms_logger* logger, char* message, char* user_uuid);
void acms_set_status_message_and_journal(acms_logger* logger, char* message, size_t size, char* user_uuid);
void acms_set_status_message(acms_logger* logger, char* message);
void acms_add_journal(acms_logger* logger, char* message, size_t size, char* user_uuid);
journal_entry* acms_logger_get_journal_head(acms_logger* logger, char* user_uuid);
log_entry* acms_alloc_log_entry(acms_logger* logger, journal_entry* jrl_head, char* user_uuid);
int acms_delete_log(acms_logger* logger, char* user_uuid, size_t ind);
void acms_cleare_logs(acms_logger* logger, char* user_uuid);
void acms_show_user_journal(acms_logger* logger, char* user_uuid);
void acms_realloc_uuid(acms_logger* logger, char* user_uuid);
#endif