import streamlit as st
import subprocess
import os
import shutil
import tempfile

# Sayfa ayarları
st.set_page_config(page_title="CyConverter 🚀", layout="wide")

# Başlık ve açıklama
st.title("🚀 CyConverter")
st.markdown("### Turn your code into a professional **Windows .exe** in seconds — right in your browser!")

# Opsiyonel girişler: Author, Icon, requirements.txt
col1, col2, col3 = st.columns(3)
with col1:
    author = st.text_input("Author Name (optional)", placeholder="e.g. Your Name or Company")
with col2:
    icon_file = st.file_uploader("Custom Icon (.ico - optional)", type=["ico"],
                                 help="Upload a .ico file to embed as your app icon")
with col3:
    requirements_file = st.file_uploader(
        "requirements.txt (optional - Python only)",
        type=["txt"],
        help="Upload if your Python code uses packages like requests, tkinter, pygame, numpy, pandas, etc."
    )

# Kod giriş yöntemi
option = st.radio("How do you want to add your code?", ("Upload File 📁", "Write Manually ✍️"), horizontal=True)

# Desteklenen diller ve uzantılar
supported_ext = {".py": "Python", ".cpp": "C++", ".cs": "C#", ".go": "Go", ".rs": "Rust"}

code = None
language = None
filename = "app"  # Varsayılan dosya adı
file_ext = ""

if option == "Upload File 📁":
    uploaded_file = st.file_uploader(
        "Drag & drop your source file",
        type=["py", "cpp", "cs", "go", "rs"],
        help="Supported: .py, .cpp, .cs, .go, .rs"
    )
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext in supported_ext:
            language = supported_ext[file_ext]
            filename = os.path.splitext(uploaded_file.name)[0]
            code = uploaded_file.getvalue().decode("utf-8")
            st.success(f"✅ {language} file loaded: **{uploaded_file.name}**")
            st.code(code, language=language.lower() if language != "C#" else "csharp")
        else:
            st.error("❌ Unsupported file type!")
            st.stop()
else:
    language = st.selectbox("Select Language", ["Python", "C++", "C#", "Go", "Rust"])
    file_ext = {"Python": ".py", "C++": ".cpp", "C#": ".cs", "Go": ".go", "Rust": ".rs"}[language]

    default_codes = {
        "Python": 'print("Hello from CyConverter! 🚀")\n# Upload requirements.txt for external packages!',
        "C++": '#include <iostream>\nint main() {\n    std::cout << "Hello from CyConverter! 🚀" << std::endl;\n    return 0;\n}',
        "C#": 'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello from CyConverter! 🚀");\n    }\n}',
        "Go": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello from CyConverter! 🚀")\n}',
        "Rust": 'fn main() {\n    println!("Hello from CyConverter! 🚀");\n}'
    }
    code = st.text_area("Paste your code here", value=default_codes[language], height=400)

# Kod yoksa durdur
if code is None or language is None:
    st.info("👆 Please upload a file or select a language and write/paste your code.")
    st.stop()

# EXE Oluştur butonu
if st.button("🚀 Build EXE & Download", type="primary", use_container_width=True):
    with st.spinner(f"Building {language} → .exe ... This may take 10–90 seconds 🔨"):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, f"{filename}{file_ext}")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Metadata hazırlığı
            final_author = author.strip() or "CyConverter User"
            description = f"Compiled from {language} using CyConverter"
            copyright_text = f"© 2025 {final_author}"

            exe_path = None
            success = False
            error_msg = ""

            try:
                if language == "Python":
                    # requirements.txt varsa paketleri kur
                    if requirements_file:
                        req_path = os.path.join(temp_dir, "requirements.txt")
                        with open(req_path, "wb") as f:
                            f.write(requirements_file.getvalue())
                        st.info("📦 Installing dependencies from requirements.txt...")
                        install_result = subprocess.run(
                            ["pip", "install", "-r", req_path],
                            capture_output=True, text=True, timeout=180
                        )
                        if install_result.returncode != 0:
                            st.error("❌ Failed to install some packages:")
                            st.code(install_result.stderr)
                            st.stop()
                        st.success("✅ All dependencies installed successfully!")

                    # PyInstaller ayarları
                    pyi_args = [
                        "pyinstaller", "--onefile", "--noconsole",
                        "--name", filename,
                        "--distpath", temp_dir,
                        source_path
                    ]

                    # Icon ekle
                    if icon_file:
                        icon_path = os.path.join(temp_dir, "app.ico")
                        with open(icon_path, "wb") as f:
                            f.write(icon_file.getvalue())
                        pyi_args += ["--icon", icon_path]

                    # Metadata (version info)
                    version_file = os.path.join(temp_dir, "file_version_info.txt")
                    version_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers=(1, 0, 0, 0), prodvers=(1, 0, 0, 0)),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringStruct(u'CompanyName', u'{final_author}'),
        StringStruct(u'FileDescription', u'{description}'),
        StringStruct(u'LegalCopyright', u'{copyright_text}'),
        StringStruct(u'ProductName', u'{filename}'),
        StringStruct(u'OriginalFilename', u'{filename}.exe')
      ])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
                    with open(version_file, "w", encoding="utf-8") as f:
                        f.write(version_content)
                    pyi_args += ["--version-file", version_file]

                    result = subprocess.run(pyi_args, capture_output=True, text=True, timeout=300)
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")

                elif language == "C++":
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")
                    result = subprocess.run([
                        "g++", source_path, "-o", exe_path,
                        "-static-libgcc", "-static-libstdc++"
                    ], capture_output=True, text=True, timeout=60)

                elif language == "C#":
                    proj_dir = os.path.join(temp_dir, "csproj")
                    os.makedirs(proj_dir, exist_ok=True)
                    csproj_content = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <SelfContained>true</SelfContained>
    <PublishSingleFile>true</PublishSingleFile>
    <PublishTrimmed>true</PublishTrimmed>
  </PropertyGroup>
</Project>'''
                    with open(os.path.join(proj_dir, f"{filename}.csproj"), "w") as f:
                        f.write(csproj_content)
                    shutil.copy(source_path, os.path.join(proj_dir, f"{filename}.cs"))
                    result = subprocess.run([
                        "dotnet", "publish", "-c", "Release", "-o", temp_dir
                    ], cwd=proj_dir, capture_output=True, text=True, timeout=180)
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")

                elif language == "Go":
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")
                    env = {**os.environ, "GOOS": "windows", "GOARCH": "amd64"}
                    result = subprocess.run([
                        "go", "build", "-o", exe_path,
                        "-ldflags", "-s -w -H=windowsgui", source_path
                    ], env=env, capture_output=True, text=True, timeout=90)

                elif language == "Rust":
                    cargo_toml = f'''[package]
name = "{filename}"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "{filename}"
path = "src/main.rs"

[profile.release]
strip = true
lto = true
'''
                    src_dir = os.path.join(temp_dir, "src")
                    os.makedirs(src_dir, exist_ok=True)
                    with open(os.path.join(temp_dir, "Cargo.toml"), "w") as f:
                        f.write(cargo_toml)
                    shutil.move(source_path, os.path.join(src_dir, "main.rs"))
                    result = subprocess.run([
                        "cargo", "build", "--release", "--target", "x86_64-pc-windows-gnu"
                    ], cwd=temp_dir, capture_output=True, text=True, timeout=240)
                    exe_path = os.path.join(temp_dir, "target", "x86_64-pc-windows-gnu", "release", f"{filename}.exe")

                # EXE var mı kontrol et
                if os.path.exists(exe_path):
                    success = True
                else:
                    error_msg = result.stderr if 'result' in locals() else "Build failed."

            except subprocess.TimeoutExpired:
                error_msg = "Build timed out — took too long."
            except Exception as e:
                error_msg = str(e)

            # Sonuç gösterimi
            if success and os.path.exists(exe_path):
                with open(exe_path, "rb") as f:
                    exe_data = f.read()
                st.success("✅ Your professional .exe is ready!")
                st.markdown(f"**Filename:** `{filename}.exe` | **Author:** `{final_author}`")
                if language == "Python" and requirements_file:
                    st.info("📦 All your Python packages are bundled inside the EXE!")
                st.download_button(
                    label="📥 Download Your EXE File",
                    data=exe_data,
                    file_name=f"{filename}.exe",
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
                st.balloons()
            else:
                st.error("❌ Build failed")
                if error_msg:
                    st.code(error_msg, language="text")

st.caption("Made with ❤️ by Sad_Always — An AlexisHQ project")
