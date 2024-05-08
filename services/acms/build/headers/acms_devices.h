enum ACMSDevice {
    ACCESS_CONTROLLER = 0,
    CARD_READER,
    LOCK,
    SENSOR,
    TURRET,
    DEVICE_MAX
};

const char* acms_get_string_name(enum ACMSDevice device);