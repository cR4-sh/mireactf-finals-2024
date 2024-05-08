#include <acms_devices.h>

const char* acms_get_string_name(enum ACMSDevice device)
{
    switch (device)
    {
    case ACCESS_CONTROLLER:
        return "Access controller";

    case CARD_READER:
        return "Smart-card reader";

    case LOCK:
        return "Electromagnetic lock";

    case SENSOR:
        return "Sensor";

    case TURRET:
        return "Machine gun turret";
    
    default:
        return "Undefined";
    }
}