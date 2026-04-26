from ..channel_manager import _parse_csv, register_channel
from .channel import MobileChannel, MobileConfig

__all__ = ["MobileChannel", "MobileConfig"]


def create_from_config(config) -> MobileChannel:
    allowed = _parse_csv(config.mobile_allowed_senders)
    return MobileChannel(
        MobileConfig(
            host=config.mobile_host or "0.0.0.0",
            port=int(config.mobile_port or 8765),
            token=config.mobile_token,
            public_base_url=config.mobile_public_base_url or "",
            allowed_senders=allowed,
        )
    )


register_channel("mobile", create_from_config)
