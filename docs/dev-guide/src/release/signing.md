*This chapter is for contributors and maintainers.*

# ISO Signing

To ensure the integrity and authenticity of the NeuralDrive images, every official release is digitally signed using GPG.

## The Signing Process

The project maintainers use a dedicated GPG key to sign the SHA256SUMS file associated with each release.

### 1. Generating Checksums
```bash
sha256sum neuraldrive-*.iso > SHA256SUMS
```

### 2. Signing the Checksum File
The maintainer signs the `SHA256SUMS` file with a detached signature:
```bash
gpg --detach-sign --armor SHA256SUMS
```
This generates a `SHA256SUMS.asc` file.

## Verification for Users

Users can verify the integrity of their download by following these steps:

### 1. Import the Public Key
The public key is available on the GitHub repository and key servers.
```bash
gpg --import neuraldrive-public.key
```

### 2. Verify the Signature
```bash
gpg --verify SHA256SUMS.asc SHA256SUMS
```
This should output "Good signature from NeuralDrive (Release Key)".

### 3. Verify the ISO
```bash
sha256sum -c SHA256SUMS --ignore-missing
```
This should output "OK" for the downloaded ISO.

## Secure Boot Signing

In addition to GPG signing for distribution, the Linux kernel and GRUB bootloader within the ISO must be signed with a Microsoft-trusted key for Secure Boot to work without manual CA installation. NeuralDrive currently uses the standard Debian Shim and GRUB binaries, which are signed by Debian's official key.

> **Warning**: Never use an ISO image that fails the checksum verification or signature check. This protects against corrupted downloads and potentially malicious tampering.

