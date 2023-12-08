# Email API
The emailing part of the pack is handled in the email_api submodule.

Emailing works by using an SMTP relay service. When the user wishes to send
emails via any of the pack email actions - our StackStorm service attempts to
connect to the relay service.

Our action builds up our email payload using templates (see below) and sends it to the service

## Templates

Since our pack is designed to send standardised emails to users - like set notifications/warnings.
We have designed templates that our emails can be constructed from.

We use [jinja2](https://jinja.palletsprojects.com/en/3.0.x/intro/) templating language to build our email templates.

Templates are stored in `email_templates`. Each template contains two versions
- in HTML format (stored in `html` directory)
- in plaintext format (stored in `plaintext` directory)

An email can be composed of one or more of these templates - but they should all be a single format - either HTML or
plaintext.


## Creating a New Template

When creating a template, you can choose whether it's HTML or plaintext or both. Its recommended
to add both so there are both options in case one of them doesn't work for whatever reason

### 1. Write the plaintext template (Recommended)

Though this is optional if you just want a HTML version - it's recommended to start with plaintext
before you write the html template

create a new file in `email_templates/plaintext/<template-name>.txt.j2`

**NOTE: remember to include the `.j2` extension so that it will be treated as a jinja2 template**

Write the body of the email. Since this is jinja2 - you can include some of the features that jinja2 gives you
see [Jinja2 Templates](https://jinja.palletsprojects.com/en/3.0.x/templates/)

One of the main features you will be using is the ability to include variables - like so:

e.g. we'll create a file called - `example.txt.j2` in `email_templates/plaintext` and write in it
```
Dear Cloud User {{username}},

Test Email
```
the `{{username}}` - refers to a variable called `username` that the template expects before being rendered. The template
will replace any instance of `{{username}}` with the value of what's stored in given `username` variable

### 2. Write the html template

You can write a html email template by writing raw HTML.

create a new file in `email_templates/html/<template-name>.html.j2`
- remember to include the `.j2` extension so that it will be treated as a jinja2 template

e.g. for `example.html.j2`
```
Dear Cloud User {{username}}; <br /><br />
Test Email
```

notice that [Jinja2 Templates](https://jinja.palletsprojects.com/en/3.0.x/templates/) will work in the same way here
- **NOTE - you'll need to make sure any variables can be rendered into proper html **

**NOTE: Working on adding CSS and styling [191](https://github.com/stfc/st2-cloud-pack/issues/191)**

### 3. Add Schema Entry

Now that the email template has been written - we need to add a reference to it in the template schema file.

The template schema file holds:
    - filepaths to the plaintext and html template files we've written
    - what variables the template expects,
    - any default values for the variables to send if not given.

The email template schema file is located in `/lib/email_api/email_template_schemas.yaml`

To add a new template, you must add another entry like so:

```yaml

...

example:   # unique name of template to refer to it in code
  schema:   # all variables are defined in schema

    # variables are listed as key-value pairs
    # unique variable name as key, default value as value
    username: null

  # relative filepaths using email_templates as root directory
  # to both html and plaintext templates - you must provide at least one - recommended both
  html_filepath: "html/test.html.j2"
  plaintext_filepath: "plaintext/test.txt.j2"

```

Now you can refer to the template when writing a new Email Action or editing an existing one.


## Interfacing with Email API

When you need to write a script to send an Email, you will need to use the Email API.

We need the following information before we try to send the email:

1. Information that make up an email:
   - email subject (Required)
   - email to send to (Required)
   - email to send from (Required)
   - whether email body is HTML or plaintext format (Required)
   - email(s) to cc in (Optional)
   - files to attach (Optional)

2. Information about the SMTP relay service
   - Information to connect to the SMTP relay service - which Mailbox to use and authentication info

3. Email Templates to use to make up the email
    - A list of jinja templates, including the variables they expect


### 1. Information that make up an email

This information is usually given by the user via the StackStorm Web UI when running the Action - usually this
information requires some validation or pre-processing - how this is done is largely left to the developer's discretion


### 2. Information about the SMTP relay service

This information should already be configured via StackStorm pack configuration.

When the action is called, a dataclass SMTPAccount is automatically created and passed through as `smtp_account`.
make sure that your Email Action YAML configuration contains the following entry to enable this. See below

```yaml
  smtp_account_name:
    type: string
    description: "Name of SMTP Account to use. Must be configured in the pack settings."
    required: true
    default: "default"
```
This entry allows the user to define the SMTP Account to use.
StackStorm will try to find any stored pack info under the  name given.
We usually leave this blank so it uses the configuration set under `default`.
See our confluence documentation on setting up the pack config

### 3. Email Template Information

This is the part that will likely change the most between Email Actions - which templates should be used to build up the email.
Usually you would write new templates for new Actions. See above about creating templates.

Once a template is created and available to use - you must define it's parameters using a dataclass called `EmailTemplateDetails`

e.g. for `example` template you define a dataclass object like so:
```python
body = EmailTemplateDetails(
    template_name="example", # set the template name

    # This sets the variables
    # if any variables that are required are not specified here - the default will be used
    # the default is specified in the schema file
    template_params={
        "username": "foo",
    },
)
```

when the email is sent, the body will contain the rendered template
```
Dear Cloud User foo,

Test Email
```

You can define more than one template this way - like so:
```python
footer = EmailTemplateDetails(
    template_name="footer"
    # footer doesn't require any variables
    template_params={}
)
```

### Tying it all-together

Once all these are created and ready to be used as stated aboce.
You must create a dataclass called `EmailParams` like so:

```python
    email_info = EmailParams(
        # we pass a list of EmailTemplateDetails dataclasses that make up the email body
        # NOTE: this will be rendered in order - here body will be rendered first, then footer
        email_templates=[body, footer],

        "subject": "subject1", # email subject
        "email_from": "from@example.com", # email address which will appear as the sender
        "email_to": "test@example.com", # email address to send to
        "email_cc": ["cc1@example.com", "cc2@example.com"], # email addresses to cc in
        "attachment_filepaths": ["path/to/file1", "path/to/file2"], # filepaths to attach (NEEDS TESTING)
        "as_html" # which template to use - if True - html, if False - plaintext (all in templates list must support given format)
    )
```

Once this is created. You can send the email.
To send emails, we use the `Emailer` class.

```python

# Emailer requires a dataclass SMTPAccount in order to be setup - this is passed automatically as a parameter
# if you're creating an action using `workflow_actions.py` as your entrypoint
# see lib/structs/email/smtp_account.py
emailer = Emailer(smtp_account)

# this send_emails method accepts a list of EmailParam dataclass objects and will iteratively send emails
# here we provide information to send a single email - hence a singleton list being used
emailer.send_emails([email_info])
```
