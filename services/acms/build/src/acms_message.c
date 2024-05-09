#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <acms_banners.h>
#include <acms_message.h>

void acms_init_logger(acms_logger* logger)
{
   memset((void*)logger, 0, sizeof(acms_logger));
   logger->shown = 1;
}

void acms_show_status_message(acms_logger* logger)
{
    if (!logger->shown)
    {
        logger->shown = 1;
        printf(STATUS_FORMAT_MESAGE, logger->msg);
    }
}

void acms_set_status_message_and_copy_journal(acms_logger* logger, char* message, char* user_uuid)
{
    acms_set_status_message(logger, message);

    size_t size = strlen(message) + 1;

    char* copy = malloc(size);
    memcpy(copy, message, size-1);
    copy[size-1] = 0;

    acms_add_journal(logger, copy, size, user_uuid);
}

void acms_set_status_message_and_journal(acms_logger* logger, char* message, size_t size, char* user_uuid)
{
    acms_set_status_message(logger, message);
    acms_add_journal(logger, message, size, user_uuid);
}

void acms_set_status_message(acms_logger* logger, char* message)
{
    size_t size = strlen(message);
    if (size > ACMS_LOG_SIZE - 1) 
        size = ACMS_LOG_SIZE - 1;

    logger->shown = 0;
    memcpy(logger->msg, message, size);
    logger->msg[size] = 0;
}

void acms_add_journal(acms_logger* logger, char* message, size_t size, char* user_uuid)
{
    journal_entry* jrl_head = acms_logger_get_journal_head(logger, user_uuid);
    if (jrl_head == NULL) return;

    log_entry* log = acms_alloc_log_entry(logger, jrl_head, user_uuid);
    if (log == NULL) return;

    log->ts = time(0);
    log->msg_size = size;
    log->msg = message;
}

journal_entry* acms_logger_get_journal_head(acms_logger* logger, char* user_uuid)
{
    journal_entry* jrl = NULL;

    if (logger->journal_head == NULL)
    {
        jrl = malloc(sizeof(journal_entry));
        memset(jrl, 0, sizeof(journal_entry));
        jrl->user_uuid = user_uuid;
        logger->journal_head = jrl;
        return jrl;
    } 

    journal_entry* last_jrl = logger->journal_head;
    
    for (jrl = logger->journal_head; jrl; jrl = jrl->next)
    {   
        if (!strcmp(jrl->user_uuid, user_uuid))
            return jrl;
        last_jrl = jrl;
    }

    jrl = malloc(sizeof(journal_entry));
    memset(jrl, 0, sizeof(journal_entry));
    jrl->user_uuid = user_uuid;
    last_jrl->next = jrl;

    return jrl;
}

log_entry* acms_alloc_log_entry(acms_logger* logger, journal_entry* jrl_entry, char* user_uuid)
{
    log_entry* log = jrl_entry->log_head;

    if (log == NULL)
    {   
        log = malloc(sizeof(log_entry));
        memset(log, 0, sizeof(log_entry));
        jrl_entry->log_head = log;
    }
    else
    {
        for (; log->next; log = log->next);
        log->next = malloc(sizeof(log_entry));
        memset(log->next, 0, sizeof(log_entry));
        log = log->next;
    }

    return log;
}

int acms_delete_log(acms_logger* logger, char* user_uuid, size_t ind)
{
    if (logger->journal_head == NULL)
        return -1;

    for(journal_entry* jrl = logger->journal_head; jrl; jrl = jrl->next)
    {
        if (strcmp(jrl->user_uuid, user_uuid) || jrl->log_head == NULL)
            continue;

        log_entry* prev_log = jrl->log_head;
        log_entry* log = jrl->log_head;

        for(; log && ind; log = log->next, ind--)
        {
            prev_log = log;
        }

        if (ind != 0)
            return -1;

        if (prev_log == log)
        {
            jrl->log_head = log->next;
        }
        else
        {
            prev_log->next = log->next;
        }
        
        free(log->msg);
        free(log);

        return 0;
    }

    return -1;
}

void acms_cleare_logs(acms_logger* logger, char* user_uuid)
{
    if (logger->journal_head == NULL)
        return;

    journal_entry* prev_jrl = logger->journal_head;
    for(journal_entry* jrl = logger->journal_head; jrl; jrl = jrl->next)
    {
        if (strcmp(jrl->user_uuid, user_uuid))
        {
            continue;
            prev_jrl = jrl;
        }

        if (jrl->log_head == NULL)
            return;

        free(jrl->user_uuid);

        log_entry* log = jrl->log_head;

        while (log)
        {
            log_entry* temp = log;
            log = temp->next;

            free(temp->msg);
            free(temp);
        }

        if (prev_jrl == jrl)
        {
            logger->journal_head = jrl->next;
        }
        else
        {
            prev_jrl->next = jrl->next;
        }

        free(jrl);

        return;
    }

    return;
}

void acms_show_user_journal(acms_logger* logger, char* user_uuid)
{
    if (logger->journal_head == NULL)
        return;

    for(journal_entry* jrl = logger->journal_head; jrl; jrl = jrl->next)
    {
        if (strcmp(jrl->user_uuid, user_uuid) || jrl->log_head == NULL)
            continue;
        
        size_t i = 1;
        for(log_entry* log = jrl->log_head; log; log = log->next)
        {
            char buffer[ACMS_LOG_SIZE + 32];
            struct tm *tm_info = localtime(&log->ts);
            strftime(buffer, 32, "[ %d/%m/%Y %H:%M:%S ]", tm_info);
            printf("%lu. %s %s\n", i, buffer, log->msg);
            i++;
        }

        break;
    }
}

void acms_realloc_uuid(acms_logger* logger, char* user_uuid)
{
    if (logger->journal_head == NULL)
        return;

    for(journal_entry* jrl = logger->journal_head; jrl; jrl = jrl->next)
    {
        if (!strcmp(jrl->user_uuid, user_uuid))
        {
            char* new_buffer = malloc(strlen(user_uuid) + 1);
            strcpy(new_buffer, user_uuid);
            jrl->user_uuid = new_buffer;
            break;
        }
    }
}