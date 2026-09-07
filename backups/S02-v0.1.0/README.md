# S02 v0.1.0 encrypted full backup

This archive preserves the complete R5-AB00-R1-S02 v0.1.0 research package, including its models and detailed evaluation artifacts. It was stored here at the project owner's request because ChatGPT Library storage was full.

**The ZIP uses AES-256 encryption.** The password is kept separately in the owner's local `S02-GITHUB-YEDEK-SIFRESI.txt` file. It is not stored in this repository. This encrypted backup is separate from the public source overlay and aggregate report; its presence does not make the enclosed research data publicly readable.

[Download the encrypted ZIP](TurkTokenizer-R5-AB00-R1-S02-v0.1.0-backup-aes256.zip?raw=true)

To restore, download the ZIP, check its SHA-256 against `SHA256SUMS`, and open it with an AES ZIP compatible archive tool such as 7-Zip using the separately retained password. Extract the inner `TurkTokenizer-R5-AB00-R1-S02-v0.1.0.zip`, then extract that package into a working directory. Its `S02-PACKAGE-MANIFEST.json` lists the hashes of the package files. The encrypted archive was decrypted locally and the recovered inner package was verified byte for byte before upload.

Encrypted file size: 7,582,248 bytes.

The S02 public source snapshot is commit `0905e7546c25597356efdabdb9f64ec9e9352ef7`. This backup is S02; later S03 experiments are not included. S02 remains an experimental version with unresolved meaning-selection errors. See [the S02 decision](../../docs/TurkTokenizer_R5_AB00_R1_S02_Decision.md) for results and limitations.
