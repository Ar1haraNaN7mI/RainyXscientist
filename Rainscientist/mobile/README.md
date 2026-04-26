# RxSci Mobile Channel

This directory contains the minimum server-side files for connecting the Android client to Rxscientist/Rainscientist.

## Files

- `mobile.config.example.yaml`: minimal config keys for the mobile channel.
- `start-mobile.ps1`: Windows launcher that writes the mobile channel config and starts `rxsci serve`.

## Quick Start

1. Choose a long random token.
2. Start the server:

```powershell
cd C:\Users\MSIK\Desktop\ChatBot\douxing\EvoScientist
.\Rainscientist\mobile\start-mobile.ps1 -Token "your-long-token" -Workdir "C:\Users\MSIK\Desktop\ChatBot\workspace"
```

3. In the Android app settings, use:

```text
Server base URL: http://<server-lan-ip>:8765
Mobile token: your-long-token
```

Use `mobile_host: 0.0.0.0` for LAN access from the phone. Keep `auto_approve: false` unless the server runs in a trusted environment.
