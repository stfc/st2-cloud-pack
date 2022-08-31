def prep_html(header: str, body: str, footer: str):
    """
    Send an email
    """
    return f"""\
            <html>
                <head>
                <style>
                    table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
                    th, td {{ padding: 8px; }}
                </style>
                </head>
                <body>
                    {header}
                    {body}
                    {footer}
                </body>
            </html>
            """
