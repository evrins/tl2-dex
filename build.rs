use std::process::Command;

fn main() {
    // Cargo caches build-script output; a new commit changes only `.git`.
    if let Some(git_dir) = git_dir() {
        println!("cargo:rerun-if-changed={git_dir}");
    }

    let hash = Command::new("git")
        .args(["rev-parse", "--short=7", "HEAD"])
        .output()
        .ok()
        .filter(|output| output.status.success())
        .and_then(|output| String::from_utf8(output.stdout).ok())
        .map(|hash| hash.trim().to_owned())
        .filter(|hash| !hash.is_empty())
        .unwrap_or_else(|| "unknown".to_owned());

    println!("cargo:rustc-env=TL2_DEX_GIT_HASH={hash}");
}

/// Absolute path to this checkout's Git directory, when it has one.
fn git_dir() -> Option<String> {
    let output = Command::new("git")
        .args(["rev-parse", "--absolute-git-dir"])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let dir = String::from_utf8(output.stdout).ok()?;
    let dir = dir.trim();
    (!dir.is_empty()).then(|| dir.to_owned())
}
