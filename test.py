import win32clipboard

def copy_html_for_outlook(html_fragment):
    CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

    fragment = html_fragment
    html = (
        "Version:0.9\r\n"
        "StartHTML:00000097\r\n"
        f"EndHTML:{97 + len(fragment)}\r\n"
        "StartFragment:00000131\r\n"
        f"EndFragment:{131 + len(fragment)}\r\n"
        "<html><body><!--StartFragment-->"
        f"{fragment}"
        "<!--EndFragment--></body></html>"
    )

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(CF_HTML, html.encode("utf-8"))
    win32clipboard.CloseClipboard()