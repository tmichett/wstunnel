# RHTLC Phase 1: Security Scanner Remediation

## Purpose

This document records the completed Phase 1 work for the Red Hat Training Lab Connector (RHTLC) tunnel executable. The goal was to make the application easier for security products and administrators to identify as a legitimate Red Hat Training component, while preserving connectivity to disposable educational classroom environments.

Phases 2–4 are intentionally outside this document. They cover broader packaging, vendor whitelisting, signing, and server hardening work and are not required for the Phase 1 assessment.

## Scope and operating context

RHTLC is used to connect learners and instructors to temporary classroom environments. The environments do not contain production data, and the tunnel is required to support easy connectivity across the classroom fleet.

The security objective for Phase 1 was not to hide tunnel behavior or bypass security controls. It was to remove avoidable identity and packaging signals that can make a legitimate classroom connector resemble an unknown dropper or malware sample:

- use a product-specific executable name;
- make the executable identity consistent at compile time, in help output, and in release artifacts;
- avoid presenting the upstream project name as the installed RHTLC component;
- make the release process deterministic and auditable;
- publish checksums for the exact executables distributed to users.

The underlying network behavior remains visible and intentional. RHTLC still performs WebSocket, HTTP/2, or WebTransport tunneling because that is the product's purpose.

## Phase 1 implementation completed

### 1. Compile-time executable rename

The CLI package now declares `rhtlc-wstunnel` as its binary name in [`wstunnel-cli/Cargo.toml`](../wstunnel-cli/Cargo.toml:30):

```toml
[[bin]]
name = "rhtlc-wstunnel"
path = "src/main.rs"
```

This is a compile-time rename, not a post-build file rename. Consequently, the produced executable, Cargo's binary target, release build commands, and artifact paths all use the RHTLC-specific name.

The library package remains named `wstunnel` because it is an internal Rust library package. That does not determine the installed CLI executable name.

### 2. User-facing CLI identity

The command-line application now identifies itself as `rhtlc-wstunnel` through the Clap command metadata in [`wstunnel-cli/src/main.rs`](../wstunnel-cli/src/main.rs:37).

The help footer identifies:

- the binary as the RHTLC tunnel transport;
- the Red Hat Training use case;
- the source repository;
- the RHTLC product repository;
- the maintainer and Red Hat Training contact.

Startup error messages were also changed to refer to `rhtlc-wstunnel` rather than the upstream executable name. This gives users, administrators, and scanner analysts a consistent product identity across process listings, command output, support tickets, and logs.

### 3. RHTLC-specific package metadata

The CLI and library manifests now contain RHTLC-specific package metadata, including:

- Red Hat Training authorship;
- RHTLC description text;
- RHTLC documentation and product links;
- the RHTLC 6.x version line;
- the BSD-3-Clause license declaration.

The relevant package manifests are [`wstunnel-cli/Cargo.toml`](../wstunnel-cli/Cargo.toml:1) and [`wstunnel/Cargo.toml`](../wstunnel/Cargo.toml:1).

This provides provenance context in the source and build metadata. It should not be confused with platform code signing; signing is not part of the completed Phase 1 work.

### 4. Release workflow switched to the RHTLC executable

The main GitHub Actions release workflow now sets [`BIN_NAME`](../.github/workflows/release.yaml:13) to `rhtlc-wstunnel` and builds explicitly with:

```text
--bin rhtlc-wstunnel
```

The build matrix currently produces the intended RHTLC artifacts for:

- Linux amd64;
- Linux arm64;
- macOS amd64;
- macOS arm64;
- Windows amd64;
- Windows arm64.

Linux builds use static musl output, which provides a predictable standalone executable suitable for the supported Linux packaging targets.

The workflow also:

- supports manual dispatch;
- uses the repository's pinned Rust version of 1.97 in CI;
- uses current checkout and artifact actions;
- avoids creating release archives that obscure the executable identity;
- publishes executable files with explicit RHTLC names.

### 5. Deterministic release asset preparation

The release workflow uses [`prepare-release-assets.sh`](../.github/scripts/prepare-release-assets.sh:1) to collect the exact CI artifacts and map them to platform-specific names such as:

```text
rhtlc-wstunnel-linux-amd64
rhtlc-wstunnel-linux-arm64
rhtlc-wstunnel-macos-amd64
rhtlc-wstunnel-macos-arm64
rhtlc-wstunnel-windows-amd64.exe
rhtlc-wstunnel-windows-arm64.exe
```

The script validates that every expected artifact directory exists, verifies that a binary is present, copies it to the release directory, sets executable permissions where supported, and creates [`checksums.sha256`](../.github/scripts/prepare-release-assets.sh:36).

This improves traceability: the executable delivered to RHTLC can be matched to a published SHA-256 checksum and to a specific CI artifact.

### 6. Legacy GoReleaser configuration updated for the new identity

The retained legacy [` .goreleaser.yaml`](../.goreleaser.yaml:1) configuration now names the generated binary `rhtlc-wstunnel`. The associated hook also searches for and replaces `rhtlc-wstunnel` artifacts in [` .goreleaser_hook.sh`](../.goreleaser_hook.sh:40).

The active release path is the direct GitHub Actions upload workflow. The GoReleaser files remain aligned with the new name so that an operator does not accidentally reintroduce an upstream-named artifact when using the legacy path.

### 7. Documentation updated for the RHTLC fork

The README now identifies the repository as an RHTLC fork and instructs users to use `rhtlc-wstunnel` rather than upstream `wstunnel`. Examples and command usage were updated accordingly, including the demo command and URL help text.

This prevents documentation, support instructions, and downloaded artifacts from presenting conflicting names.

## How the changes address the scanner concern

The reported scanner event included an executable called `wstunnel` launched from a PyInstaller temporary extraction directory. Phase 1 addresses the executable identity portion of that event:

```text
wstunnel  ->  rhtlc-wstunnel
```

The new name communicates that the executable is an RHTLC component rather than an anonymous upstream tunneling utility. It also gives security teams a stable product name to document, approve, monitor, and associate with the RHTLC parent application.

The release process now supplies additional evidence that can be used during review:

1. The binary name is consistent from Cargo compilation through release publication.
2. The CLI help identifies the RHTLC product and source repositories.
3. Package metadata identifies Red Hat Training ownership and documentation.
4. Release artifacts use explicit platform names.
5. SHA-256 checksums are generated for the exact published executables.
6. The build is reproducible at the workflow level from a tagged source revision and declared Rust toolchain.

These changes are intended to reduce false positives caused by an unfamiliar filename, inconsistent product identity, or poorly traceable release artifact.

## What Phase 1 does not claim

Phase 1 does not guarantee that all security scanners will classify the executable as benign. The application intentionally has behaviors that can trigger generic tunneling or proxy detections:

- encrypted WebSocket/HTTP/QUIC traffic;
- TCP and UDP forwarding;
- SOCKS5 and HTTP proxy support;
- connections to classroom endpoints selected at runtime.

Those are functional requirements, not attempts to conceal malicious activity. A scanner may still classify the program as a tunneling tool, hacktool, riskware, or potentially unwanted application based on behavior alone.

Phase 1 also does not yet provide:

- Authenticode signing for Windows;
- Apple code signing or notarization;
- Linux package signing;
- vendor false-positive submissions or allowlisting;
- replacement of PyInstaller one-file extraction in the RHTLC GUI;
- changes to the JWT design, TLS verification defaults, server restrictions, or other broader security controls.

Those items are deliberately deferred because the current request is limited to the completed Phase 1 work and scanner-facing identity improvements.

## Recommended evidence package for scanner review

When distributing a release or responding to a scanner alert, provide:

- the RHTLC release URL;
- the exact platform and version;
- the SHA-256 checksum from `checksums.sha256`;
- the RHTLC product repository URL;
- the source repository and tagged commit;
- the expected parent process, `rhtlc-gui`;
- the expected child process, `rhtlc-wstunnel`;
- the classroom endpoint or endpoint pattern used for the test;
- a statement that the application is used only for disposable educational labs.

The expected process relationship should now look like:

```text
rhtlc-gui
└── rhtlc-wstunnel client ...
```

The executable should be installed and launched from the normal RHTLC installation directory rather than from an unexplained temporary path wherever the RHTLC packaging permits it. The executable rename alone cannot change a PyInstaller one-file parent's extraction behavior; that is a separate packaging concern.

## Phase 1 conclusion

Phase 1 successfully establishes a distinct, consistent, and auditable RHTLC tunnel identity. It removes the avoidable upstream `wstunnel` name from the compiled CLI and release artifacts, adds product ownership and provenance information, simplifies release artifact handling, and publishes checksums.

These measures improve trust and make a scanner alert easier to investigate without weakening security controls or attempting to disguise the application's required tunneling behavior. They are the appropriate first response for an educational connector whose functionality must remain broad enough to reach all supported disposable classroom environments.
