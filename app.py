import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="CyConverter4Python 🚀", layout="wide")

st.title("🚀 CyConverter4Python")
st.markdown("### Convert your Python code to a professional **Windows .exe** — instantly in your browser!")

# Optional features
col1, col2, col3 = st.columns(3)
with col1:
    author = st.text_input("Author Name (optional)", placeholder="Your name or company")
with col2:
    icon_file = st.file_uploader("Custom Icon (.ico - optional)", type=["ico"])
with col3:
    requirements_file = st.file_uploader(
        "requirements.txt (optional)",
        type=["txt"],
        help="Upload if you use packages like requests, tkinter, pygame, pandas, selenium, etc."
    )

# Code input
option = st.radio("How do you want to add your Python code?", ("Upload .py file 📁", "Write manually ✍️"), horizontal=True)

code = None
filename = "myapp"

if option == "Upload .py file 📁":
    uploaded_file = st.file_uploader("Upload your main Python file (.py)", type=["py"])
    if uploaded_file is not None:
        filename = os.path.splitext(uploaded_file.name)[0]
        code = uploaded_file.getvalue().decode("utf-8")
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        st.code(code, language="python")
else:
    code = st.text_area(
        "Paste or write your Python code here",
        value='# Hello!\nprint("I became an EXE with CyConverter4Python! 🚀")\n# Upload requirements.txt to add any package',
        height=400
    )

if code is None:
    st.info("👆 Please upload a .py file or write your code.")
    st.stop()

if st.button("🚀 Build EXE & Download", type="primary", use_container_width=True):
    with st.spinner("Building your .exe — this may take 20-60 seconds 🔨"):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, f"{filename}.py")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            final_author = author.strip() or "CyConverter4Python User"
            description = "Created with CyConverter4Python"
            copyright_text = f"© 2025 {final_author}"

            # Install packages if requirements.txt uploaded
            if requirements_file:
                req_path = os.path.join(temp_dir, "requirements.txt")
                with open(req_path, "wb") as f:
                    f.write(requirements_file.getvalue())
                st.info("📦 Installing packages from requirements.txt...")
                install_result = subprocess.run(["pip", "install", "-r", req_path], capture_output=True, text=True, timeout=180)
                if install_result.returncode != 0:
                    st.error("Some packages failed to install:")
                    st.code(install_result.stderr)
                    st.stop()
                st.success("✅ All packages installed successfully!")

            # PyInstaller command (normal, no cross-compile)
            pyi_args = [
                "pyinstaller", "--onefile", "--noconsole",
                "--name", filename,
                "--distpath", temp_dir,
                source_path
            ]

            if icon_file:
                icon_path = os.path.join(temp_dir, "icon.ico")
                with open(icon_path, "wb") as f:
                    f.write(icon_file.getvalue())
                pyi_args += ["--icon", icon_path]

            version_file = os.path.join(temp_dir, "version_info.txt")
            version_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers=(1,0,0,0), prodvers=(1,0,0,0)),
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
    VarFileInfo([VarStruct(u'Translation', [1033,1200])])
  ]
)'''
            with open(version_file, "w", encoding="utf-8") as f:
                f.write(version_content)
            pyi_args += ["--version-file", version_file]

            result = subprocess.run(pyi_args, capture_output=True, text=True, timeout=300)
            exe_path = os.path.join(temp_dir, f"{filename}.exe")

            if os.path.exists(exe_path):
                with open(exe_path, "rb") as f:
                    exe_data = f.read()
                st.success("✅ Your .exe has been successfully built!")
                st.markdown(f"**Filename:** `{filename}.exe` | **Author:** `{final_author}`")
                if requirements_file:
                    st.info("📦 All your packages are bundled inside the EXE!")
                st.download_button(
                    "📥 Download Your EXE File",
                    exe_data,
                    file_name=f"{filename}.exe",
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
                st.balloons()
            else:
                st.error("❌ Build failed")
                st.code(result.stderr or result.stdout)

st.caption("Made with ❤️ by Sad_Always — An AlexisHQ project | Python → Professional Windows EXE")
