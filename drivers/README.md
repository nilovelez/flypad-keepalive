# ViGEmBus driver

Flypad Keepalive creates a virtual Xbox 360 controller through the **ViGEmBus** driver. The program
does not install it: it has to be installed once on each PC before using it.

Included installer: `ViGEmBus_1.22.0_x64_x86_arm64.exe` (for x64, x86 and ARM64; Windows 10 and 11).
Run it, go through the steps and restart if asked to.

A copy is kept here because ViGEmBus has been discontinued by its author since 2023 and the original
download could disappear.

## Provenance

| | |
|---|---|
| Version | v1.22.0 |
| Source | https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0 |
| Size | 6,278,576 bytes |
| SHA-256 | `89220A7865076B342892F98865F3499FB7C4CFD673159E89D352C360FD014C6A` |
| Signature | Valid Authenticode signature, Nefarius Software Solutions e.U. |

To check that the file hasn't changed (PowerShell):

```powershell
Get-FileHash .\ViGEmBus_1.22.0_x64_x86_arm64.exe -Algorithm SHA256
```

## License

ViGEmBus is © Nefarius Software Solutions e.U. and is redistributed under the BSD 3-Clause License;
see [LICENSE-ViGEmBus.txt](LICENSE-ViGEmBus.txt).
