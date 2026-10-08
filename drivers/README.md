# Driver ViGEmBus

Flypad Keepalive crea un mando virtual de Xbox 360 a través del driver **ViGEmBus**. El programa
no lo instala: hay que instalarlo una vez en cada PC, antes de usarlo.

Instalador incluido: `ViGEmBus_1.22.0_x64_x86_arm64.exe` (válido para x64, x86 y ARM64; Windows 10 y 11).
Ejecútalo, acepta los pasos y reinicia si te lo pide.

Se guarda una copia aquí porque ViGEmBus está descontinuado por su autor desde 2023 y la descarga
original podría desaparecer.

## Procedencia

| | |
|---|---|
| Versión | v1.22.0 |
| Origen | https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0 |
| Tamaño | 6 278 576 bytes |
| SHA-256 | `89220A7865076B342892F98865F3499FB7C4CFD673159E89D352C360FD014C6A` |
| Firma | Authenticode válida, Nefarius Software Solutions e.U. |

Para comprobar que el archivo no ha cambiado (PowerShell):

```powershell
Get-FileHash .\ViGEmBus_1.22.0_x64_x86_arm64.exe -Algorithm SHA256
```

## Licencia

ViGEmBus es © Nefarius Software Solutions e.U. y se redistribuye bajo la licencia BSD de 3 cláusulas;
ver [LICENSE-ViGEmBus.txt](LICENSE-ViGEmBus.txt).
