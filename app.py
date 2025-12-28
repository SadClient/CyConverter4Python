import streamlit as st
import subprocess
import os
import shutil
import tempfile

st.set_page_config(page_title="Code to EXE 🚀", layout="centered")

st.title("🚀 Code to EXE Converter")
st.markdown("Upload or write code in **Python • C++ • C# • Go • Rust** and get a standalone **Windows .exe** file in seconds!")

# Option: Upload file or write manually
option = st.radio("How do you want to add your code?", ("Upload File 📁", "Write Manually ✍️"))

supported_ext = {
    ".py": "Python",
    ".cpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust"
}

code = None
language = None
filename = "main"
file_ext = ""

if option == "Upload File 📁":
    uploaded_file = st.file_uploader(
        "Drag & drop or select your source file (.py, .cpp, .cs, .go, .rs)",
        type=["py", "cpp", "cs", "go", "rs"]
    )
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext in supported_ext:
            language = supported_ext[file_ext]
            filename = os.path.splitext(uploaded_file.name)[0]
            code = uploaded_file.getvalue().decode("utf-8")
            st.success(f"✅ {language} file uploaded: **{uploaded_file.name}**")
            st.code(code, language=language.lower() if language != "C#" else "csharp")
        else:
            st.error("❌ Unsupported file type!")
            st.stop()
else:
    language = st.selectbox("Select Language", ["Python", "C++", "C#", "Go", "Rust"])
    file_ext = {"Python": ".py", "C++": ".cpp", "C#": ".cs", "Go": ".go", "Rust": ".rs"}[language]

    default_codes = {
        "Python": 'print("Hello World! 🚀")',
        "C++": '#include <iostream>\nint main() {\n    std::cout << "Hello World! 🚀" << std::endl;\n    return 0;\n}',
        "C#": 'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello World! 🚀");\n    }\n}',
        "Go": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello World! 🚀")\n}',
        "Rust": 'fn main() {\n    println!("Hello World! 🚀");\n}'
    }
    code = st.text_area("Paste your code here", value=default_codes[language], height=400)

if code is None or language is None:
    st.info("👆 Please upload a file or select a language and write code.")
    st.stop()

if st.button("🚀 Build EXE & Download", type="primary"):
    with st.spinner(f"Compiling {language} code... This may take a moment 🔨"):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, f"{filename}{file_ext}")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            exe_path = None
            error_msg = ""
            success = False

            try:
                if language == "Python":
                    result = subprocess.run([
                        "pyinstaller", "--onefile", "--noconsole",
                        "--distpath", temp_dir, source_path
                    ], capture_output=True, timeout=120)
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")

                elif language == "C++":
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")
                    result = subprocess.run([
                        "g++", source_path, "-o", exe_path, "-static-libgcc", "-static-libstdc++"
                    ], capture_output=True, timeout=60)

                elif language == "C#":
                    proj_dir = os.path.join(temp_dir, "csproj")
                    os.makedirs(proj_dir)
                    csproj = f'''
<Project Sdk="Microsoft.NET.Sdk">
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
                        f.write(csproj)
                    shutil.copy(source_path, os.path.join(proj_dir, f"{filename}.cs"))
                    result = subprocess.run([
                        "dotnet", "publish", "-c", "Release", "-o", temp_dir
                    ], cwd=proj_dir, capture_output=True, timeout=120)
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")

                elif language == "Go":
                    exe_path = os.path.join(temp_dir, f"{filename}.exe")
                    env = {**os.environ, "GOOS": "windows", "GOARCH": "amd64"}
                    result = subprocess.run([
                        "go", "build", "-o", exe_path,
                        "-ldflags", "-s -w -H=windowsgui", source_path
                    ], env=env, capture_output=True, timeout=60)

                elif language == "Rust":
                    cargo_toml = '''
[package]
name = "app"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "app"
path = "main.rs"
'''
                    os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
                    with open(os.path.join(temp_dir, "Cargo.toml"), "w") as f:
                        f.write(cargo_toml)
                    shutil.move(source_path, os.path.join(temp_dir, "src", "main.rs"))
                    result = subprocess.run([
                        "cargo", "build", "--release", "--target", "x86_64-pc-windows-gnu"
                    ], cwd=temp_dir, capture_output=True, timeout=180)
                    exe_path = os.path.join(temp_dir, "target", "x86_64-pc-windows-gnu", "release", f"{filename}.exe")

                if os.path.exists(exe_path):
                    success = True
                else:
                    error_msg = result.stderr.decode("utf-8", errors="replace") if result else "Unknown error"

            except Exception as e:
                error_msg = str(e)

            if success:
                with open(exe_path, "rb") as f:
                    exe_data = f.read()
                st.success("✅ EXE built successfully!")
                st.download_button(
                    "📥 Download EXE File",
                    exe_data,
                    file_name=f"{filename}.exe",
                    mime="application/octet-stream",
                    type="primary"
                )
                st.balloons()
            else:
                st.error("❌ Build failed:")
                st.code(error_msg or "An unknown error occurred.", language="text")
