import logging
import threading


class CECController:
    def __init__(self, karaoke):
        self.karaoke = karaoke
        self.lib = None
        self._key_actions = {}

    def start(self):
        try:
            import cec as _cec
            self._cec = _cec
        except ImportError:
            logging.warning("CEC: python3-cec not available, CEC disabled")
            return False

        threading.Thread(target=self._init_adapter, daemon=True).start()
        return True

    def _detect_port(self):
        """Use a callback-free lib to find which adapter has an active TV."""
        cec = self._cec

        cfg = cec.libcec_configuration()
        cfg.strDeviceName = "pikaraoke-detect"
        cfg.bActivateSource = 0
        cfg.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        cfg.clientVersion = cec.LIBCEC_VERSION_CURRENT

        probe = cec.ICECAdapter.Create(cfg)
        adapters = probe.DetectAdapters()

        found = None
        for adapter in adapters:
            port = adapter.strComName
            logging.debug(f"CEC: Probing {port}")
            if not probe.Open(port):
                logging.debug(f"CEC: Could not open {port}")
                continue
            status = probe.GetDevicePowerStatus(cec.CECDEVICE_TV)
            probe.Close()
            if status != cec.CEC_POWER_STATUS_UNKNOWN:
                logging.info(f"CEC: TV found on {port} (power status: {status})")
                found = port
                break
            logging.debug(f"CEC: No TV on {port}")

        return found

    def _init_adapter(self):
        cec = self._cec
        k = self.karaoke

        port = self._detect_port()
        if port is None:
            logging.error("CEC: No adapter with an active TV found, CEC disabled")
            return

        self._key_actions = {
            cec.CEC_USER_CONTROL_CODE_PLAY:                k.pause,
            cec.CEC_USER_CONTROL_CODE_PLAY_FUNCTION:       k.pause,
            cec.CEC_USER_CONTROL_CODE_PAUSE:               k.pause,
            cec.CEC_USER_CONTROL_CODE_PAUSE_PLAY_FUNCTION: k.pause,
            cec.CEC_USER_CONTROL_CODE_STOP:                k.skip,
            cec.CEC_USER_CONTROL_CODE_STOP_FUNCTION:       k.skip,
            cec.CEC_USER_CONTROL_CODE_FAST_FORWARD:        k.skip,
            cec.CEC_USER_CONTROL_CODE_FORWARD:             k.skip,
            cec.CEC_USER_CONTROL_CODE_REWIND:              k.restart,
            cec.CEC_USER_CONTROL_CODE_BACKWARD:            k.restart,
            cec.CEC_USER_CONTROL_CODE_VOLUME_UP:           k.vol_up,
            cec.CEC_USER_CONTROL_CODE_VOLUME_DOWN:         k.vol_down,
        }

        cfg = cec.libcec_configuration()
        cfg.strDeviceName = "pikaraoke"
        cfg.bActivateSource = 0
        cfg.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        cfg.clientVersion = cec.LIBCEC_VERSION_CURRENT
        cfg.SetLogCallback(self._on_log)
        cfg.SetKeyPressCallback(self._on_key_press)

        self.lib = cec.ICECAdapter.Create(cfg)
        if not self.lib.Open(port):
            logging.error(f"CEC: Failed to open {port} with callbacks")
            self.lib = None
            return

        logging.info(f"CEC: Ready on {port}")

    def wake_and_activate(self):
        if self.lib:
            self.lib.PowerOnDevices(self._cec.CECDEVICE_TV)
            self.lib.SetActiveSource()

    def standby_tv(self):
        if self.lib:
            self.lib.StandbyDevices(self._cec.CECDEVICE_BROADCAST)

    def shutdown(self):
        if self.lib:
            self.lib.Close()
            self.lib = None

    def _on_key_press(self, key, duration):
        # duration=0 is the initial press; >0 is the release with hold duration
        if duration > 0:
            return 0
        action = self._key_actions.get(key)
        if action:
            logging.debug(f"CEC key {key} -> {action.__name__}")
            action()
        return 0

    def _on_log(self, level, time, message):
        cec = self._cec
        if level == cec.CEC_LOG_ERROR:
            logging.error(f"CEC: {message}")
        elif level == cec.CEC_LOG_WARNING:
            logging.warning(f"CEC: {message}")
        return 0
