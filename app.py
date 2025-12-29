import streamlit as st
import subprocess
import os
import shutil
import tempfile

st.set_page_config(page_title="CyConverter 🚀", layout="wide")

st.title("🚀 CyConverter")
st.markdown("### Convert code from **Python • C++ • C# • Go • Rust** to real **Windows .exe** — instantly in your browser!")

# Optional inputs
col1, col2 = st.columns(2)
with col1:
    author = st.text_input("Author Name (optional)", placeholder="Your name or company")
with col2:
    icon_file = st.file_uploader("Custom Icon (.ico - optional)", type=["ico"])

# Language selection
language = st.selectbox("Select Language", ["Python", "C++", "C#", "Go", "Rust"])

# Code input method
option = st.radio("How do you want to add your code?", ("Upload File 📁", "Write Manually ✍️"), horizontal=True)

supported_ext = {".py": "Python", ".cpp": "C++", ".cs": "C#", ".go": "Go", ".rs": "Rust"}
code = None
filename = "app"
file_ext = {"Python": ".py", "C++": ".cpp", "C#": ".cs", "Go": ".go", "Rust": ".rs"}[language]

if option == "Upload File 📁":
    uploaded_file = st.file_uploader(f"Upload your {language} source file", type=[file_ext[1:]])
    if uploaded_file is not None:
        filename = os.path.splitext(uploaded_file.name)[0]
        code = uploaded_file.getvalue().decode("utf-8")
        st.success(f"✅ {language} file uploaded: **{uploaded_file.name}**")
        st.code(code, language=language.lower() if language != "C#" else "csharp")
else:
    default_codes = {
        "Python": 'print("Hello from CyConverter! 🚀")\nprint("Real Windows EXE!")',
        "C++": '#include <iostream>\nint main() {\n    std::cout << "Hello from CyConverter! 🚀" << std::endl;\n    return 0;\n}',
        "C#": 'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello from CyConverter! 🚀");\n    }\n}',
        "Go": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello from CyConverter! 🚀")\n}',
        "Rust": 'fn main() {\n    println!("Hello from CyConverter! 🚀");\n}'
    }
    code = st.text_area("Paste your code here", value=default_codes[language], height=400)

if code is None:
    st.info("👆 Please upload a file or write your code.")
    st.stop()

if st.button("🚀 Build Windows EXE & Download", type="primary", use_container_width=True):
    with st.spinner(f"Building {language} → Windows .exe ..."):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, f"{filename}{file_ext}")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            final_author = author.strip() or "CyConverter User"
            success = False
            error_msg = ""
            exe_data = None
            final_exe_path = None

            try:
                exe_path = os.path.join(temp_dir, f"{filename}.exe")
                if language == "Python":
                    pyi_args = ["wine", "pyinstaller", "--onefile", "--noconsole", "--distpath", temp_dir, source_path]
                    if icon_file:
                        icon_path = os.path.join(temp_dir, "icon.ico")
                        with open(icon_path, "wb") as f:
                            f.write(icon_file.getvalue())
                        pyi_args += ["--icon", icon_path]
                    result = subprocess.run(pyi_args, capture_output=True, text=True, timeout=400)

                elif language == "C++":
                    result = subprocess.run([
                        "x86_64-w64-mingw32-g++", source_path, "-o", exe_path, "-static"
                    ], capture_output=True, text=True, timeout=60)

                elif language == "C#":
                    proj_dir = os.path.join(temp_dir, "csproj")
                    os.makedirs(proj_dir, exist_ok=True)
                    csproj_content = '<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net8.0</TargetFramework>\n    <RuntimeIdentifier>win-x64</RuntimeIdentifier>\n    <SelfContained>true</SelfContained>\n    <PublishSingleFile>true</PublishSingleFile>\n    <PublishTrimmed>true</PublishTrimmed>\n  </PropertyGroup>\n</Project>'
                    with open(os.path.join(proj_dir, f"{filename}.csproj"), "w") as f:
                        f.write(csproj_content)
                    shutil.copy(source_path, os.path.join(proj_dir, f"{filename}.cs"))
                    result = subprocess.run([
                        "dotnet", "publish", "-c", "Release", "-r", "win-x64", "--self-contained", "true", "-p:PublishSingleFile=true", "-o", temp_dir
                    ], cwd=proj_dir, capture_output=True, text=True, timeout=180)

                elif language == "Go":
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")
                    env = {**os.environ, "GOOS": "windows", "GOARCH": "amd64"}
                    result = subprocess.run([
                        "go", "build", "-o", exe_path, "-ldflags", "-s -w -H=windowsgui", source_path
                    ], env=env, capture_output=True, text=True, timeout=90)

                elif language == "Rust":
                    cargo_toml = f'[package]\nname = "{filename}"\nversion = "0.1.0"\nedition = "2021"\n\n[[bin]]\nname = "{filename}"\npath = "src/main.rs"'
                    src_dir = os.path.join(temp_dir, "src")
                    os.makedirs(src_dir, exist_ok=True)
                    with open(os.path.join(temp_dir, "Cargo.toml"), "w") as f:
                        f.write(cargo_toml)
                    shutil.move(source_path, os.path.join(src_dir, "main.rs"))
                    result = subprocess.run([
                        "cargo", "build", "--release", "--target", "x86_64-pc-windows-gnu"
                    ], cwd=temp_dir, capture_output=True, text=True, timeout=240)
                    exe_path = os.path.join(temp_dir, "target", "x86_64-pc-windows-gnu", "release", f"{filename}.exe")

                # EXE'yi her olası konumdan ara (Wine/PyInstaller farklı yerlere koyabiliyor)
                possible_paths = [
                    os.path.join(temp_dir, "dist", f"{filename}.exe"),
                    os.path.join(temp_dir, "dist", filename),
                    os.path.join(temp_dir, f"{filename}.exe"),
                    os.path.join(temp_dir, filename),
                    exe_path if 'exe_path' in locals() else None
                ]

                for p in possible_paths:
                    if p and os.path.exists(p):
                        final_exe_path = p
                        with open(p, "rb") as f:
                            exe_data = f.read()
                        success = True
                        break

                if not success:
                    error_msg = result.stderr if 'result' in locals() else "No executable found"

            except Exception as e:
                error_msg = str(e)

            if success:
                st.success("✅ Real Windows .exe built successfully!")
                st.markdown(f"**Language:** {language} | **Filename:** `{os.path.basename(final_exe_path)}` | **Author:** `{final_author}`")
                st.download_button(
                    "📥 Download Windows EXE",
                    exe_data,
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

st.caption("Made with ❤️ by Sad_Always — An AlexisHQ project | Multi-language → Real Windows EXE")
