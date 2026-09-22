# Basic Repo

**Basic Repo** is a lightweight graphical package and repository manager
for Fedora.

It provides a clean dark interface for common DNF and RPM tasks,
including package browsing, updates, local RPM installation, repository
management, and automatic repository health checking.

> Basic Repo is currently focused on Fedora and Fedora-based systems.

## Features

### Package management

-   Browse installed packages
-   Browse available packages
-   Search packages by name
-   View available updates
-   View package information
-   Install packages
-   Remove installed packages
-   Update individual packages
-   Update the entire system
-   Install local `.rpm` files
-   Refresh DNF metadata

### Repository management

-   View repositories from `/etc/yum.repos.d/`
-   See whether a repository is enabled or disabled
-   View repository names and configuration files
-   View `baseurl`, `metalink`, and `mirrorlist` sources
-   Add new `.repo` files
-   Enable repositories
-   Disable repositories
-   Delete individual repository sections
-   Preserve other repository sections stored in the same `.repo` file
-   Create a backup before deleting a repository section

### Repository health checking

Basic Repo can ask DNF to test repositories individually instead of
simply checking whether a website responds.

This matters because Fedora repositories can use base URLs, mirror
lists, metalinks, and DNF-specific metadata.

The checker can identify problems including:

-   HTTP `401 Unauthorized`
-   HTTP `403 Forbidden`
-   HTTP `404 Not Found`
-   HTTP `410 Gone`
-   HTTP `5xx` server errors
-   No usable repository URL
-   Missing or inaccessible `repomd.xml`
-   Metadata download failures
-   DNS resolution failures
-   Connection failures
-   Timeouts
-   TLS/SSL certificate problems
-   cURL/download errors

For example, output such as:

``` text
Status code: 403 for https://example.com/repodata/repomd.xml
Usable URL not found
```

is reported as a repository problem instead of being treated as a
successful check.

### Automatic health monitoring

Basic Repo can automatically check enabled repositories in the
background.

The default configuration:

-   waits **30 seconds** after startup before the first automatic check
-   checks enabled repositories
-   reports detected problems
-   repeats the check every **30 minutes**

Automatic checking does **not** automatically delete or disable a
repository. A temporary network outage, DNS issue, or server maintenance
should not silently modify the user's system configuration.


## Requirements

Basic Repo currently requires:

-   Fedora or a compatible Fedora-based Linux distribution
-   Python 3
-   Tkinter
-   DNF
-   RPM
-   PolicyKit / `pkexec`

The application uses the system's existing DNF and RPM tools rather than
implementing its own package-management backend.

## Installation

Clone or download the project, then install the Tkinter dependency:

``` bash
sudo dnf install python3-tkinter
```

Make sure the required commands are available:

``` bash
dnf --version
rpm --version
pkexec --version
python3 --version
```

## Running

If the main file is named `package.py`:

``` bash
python3 package.py
```

You can also make it executable:

``` bash
chmod +x package.py
./package.py
```

Before running a modified version, you can quickly check its Python
syntax:

``` bash
python3 -m py_compile package.py
```

No output means the syntax check completed successfully.

## Usage

### Browse installed packages

Open **Installed** from the sidebar.

Basic Repo reads installed package information from RPM and displays the
package name, version, architecture, and installation status.

### Browse available packages

Open **Available** to query DNF for packages available from configured
repositories.

### Search

Enter a package name in the search field and press **Enter**.

Basic Repo asks DNF for matching packages and displays the results in
the package list.

### Check for updates

Open **Updates** to view packages for which DNF reports an available
update.

### Install a package

Select an available package and choose **Install**.

Basic Repo uses `pkexec` to request administrator authorization before
performing the DNF transaction.

### Remove a package

Select an installed package and choose **Remove**.

DNF remains responsible for calculating dependency changes.

### Update a package

Select an installed package and choose **Update**.

### Update the system

Choose **Update All** from the sidebar.

Basic Repo asks for confirmation and administrator authorization before
starting the upgrade.

### Install a local RPM

Choose **Install RPM**, select a `.rpm` file, and confirm the operation.

The RPM is installed through DNF so normal dependency handling is
retained.

## Working with repositories

Open **Repositories** from the sidebar.

Basic Repo reads repository definitions from:

``` text
/etc/yum.repos.d/
```

Select a repository to view its configuration and available actions.

### Check one repository

Select a repository and choose **Check Health**.

Basic Repo temporarily asks DNF to use only that repository while
refreshing its metadata.

Conceptually, the check is equivalent to:

``` bash
dnf --disablerepo='*' --enablerepo='<repo-id>' makecache --refresh
```

The DNF output is inspected for known HTTP, metadata, DNS, TLS, timeout,
and network failures.

### Check all repositories

Choose **Check All**.

Only enabled repositories are checked. Basic Repo tests them one at a
time and reports any problems it finds.

### Enable or disable a repository

Select a repository and choose **Enable** or **Disable**.

Administrator authorization is required because repository definitions
are normally stored under `/etc`.

### Delete a repository

Select a repository and choose **Delete**.

Basic Repo removes the selected repository section rather than blindly
deleting the complete `.repo` file. This is important because one file
can contain multiple repository definitions.

A `.basicrepo.bak` backup is created before the repository section is
removed.

### Add a repository

Choose **Add .repo File** and select a repository configuration file.

Basic Repo copies it into:

``` text
/etc/yum.repos.d/
```

Administrator authorization is required.

## Automatic repository checking

Automatic checking is controlled by constants near the top of the Python
source:

``` python
AUTO_REPO_CHECK = True

AUTO_CHECK_START_DELAY = 30 * 1000

AUTO_CHECK_INTERVAL = 30 * 60 * 1000
```

The values passed to Tkinter's `after()` method are milliseconds.

To disable automatic checking:

``` python
AUTO_REPO_CHECK = False
```

To run the first check after 60 seconds:

``` python
AUTO_CHECK_START_DELAY = 60 * 1000
```

To check once per hour:

``` python
AUTO_CHECK_INTERVAL = 60 * 60 * 1000
```

## Why repository checks use DNF

A repository is more than a normal website.

A simple HTTP request to the repository's homepage is not enough to
determine whether DNF can actually use it. Repositories may depend on:

-   `repodata/repomd.xml`
-   metalinks
-   mirror lists
-   architecture-specific paths
-   Fedora release variables
-   DNF metadata behavior

Basic Repo therefore lets DNF perform the repository check and analyzes
the result.

## Permissions

Normal browsing and health checks do not require Basic Repo itself to
run as root.

Operations that modify the system use `pkexec`, including package
installation and repository configuration changes.

**Do not run the entire GUI with `sudo` unless you are debugging a
specific issue.**

Keeping the normal GUI unprivileged and elevating only operations that
require administrator access reduces unnecessary root execution.

## Safety

Repository configuration can affect system updates and package
installation.

Before deleting or modifying important repositories:

1.  Verify that you recognize the repository.
2.  Prefer disabling an uncertain repository before deleting it.
3.  Remember that a temporary HTTP, DNS, TLS, or timeout failure does
    not necessarily mean the repository is permanently dead.
4.  Keep backups of important custom repository definitions.

Basic Repo intentionally does not automatically delete a repository
simply because a health check fails.

## Troubleshooting

### The application does not start

Check the Python syntax:

``` bash
python3 -m py_compile package.py
```

Then run it from a terminal so errors remain visible:

``` bash
python3 package.py
```

### `tkinter` is missing

Install it with:

``` bash
sudo dnf install python3-tkinter
```

### `pkexec` is missing

Check:

``` bash
which pkexec
```

Basic Repo needs PolicyKit authentication for privileged package and
repository operations.

### A repository reports 403

HTTP `403 Forbidden` means the server received the request but refused
access.

Basic Repo reports this as a repository problem. It does not assume the
repository should immediately be deleted.

### A repository reports 404

HTTP `404 Not Found` commonly means the configured repository path or
metadata location no longer exists.

Check whether the repository provider has published a new Fedora
repository URL before deleting the old configuration.

### `Usable URL not found`

This indicates that DNF could not obtain a usable source for the
repository. The underlying cause may be an HTTP error, broken mirror
configuration, invalid URL, or unavailable metadata.

### Repository check times out

The current checker uses a timeout so one dead repository cannot block
the application indefinitely.

A timeout can also be caused by a slow network or temporarily
unavailable mirror.

### Package lists look incomplete

Basic Repo currently parses the command-line output produced by DNF. DNF
output and behavior can differ between releases.

Improving DNF4/DNF5 compatibility is an area for future development.

## Current project structure

The current version is intentionally simple:

``` text
basic-repo/
├── package.py
├── README.md
└── LICENSE
```

As the project grows, it can be split into separate modules:

``` text
basic-repo/
├── basic_repo.py
├── basicrepo/
│   ├── __init__.py
│   ├── ui.py
│   ├── packages.py
│   ├── repositories.py
│   ├── transactions.py
│   └── theme.py
├── assets/
├── screenshots/
├── README.md
├── LICENSE
└── pyproject.toml
```

## Current limitations

Basic Repo is still an early project.

Current limitations include:

-   Fedora-focused
-   Tkinter-based interface
-   DNF output parsing may need adjustments across DNF versions
-   Repository health checks are sequential
-   Repository status is not yet stored between application sessions
-   Package search is currently basic
-   No transaction history interface yet
-   No Flatpak management yet
-   No COPR-specific management interface yet
-   No system tray notifications yet

## Roadmap

Ideas for future releases:

-   [ ] Better DNF5 integration
-   [ ] Live package search/filtering
-   [ ] Repository health indicators directly in the repository list
-   [ ] Last-checked timestamps
-   [ ] Background notifications for broken repositories
-   [ ] Package transaction progress
-   [ ] Download progress
-   [ ] Transaction history
-   [ ] Repository repair suggestions
-   [ ] COPR management
-   [ ] Flatpak support
-   [ ] Package categories
-   [ ] Package icons
-   [ ] Improved package descriptions
-   [ ] Configurable automatic-check interval
-   [ ] Settings page
-   [ ] Light/dark theme selection
-   [ ] Localization
-   [ ] Modular codebase
-   [ ] RPM packaging for Basic Repo itself

## Contributing

Contributions are welcome.

If you want to contribute:

1.  Fork the repository.
2.  Create a branch for your change.
3.  Keep changes focused and readable.
4.  Test package operations on Fedora.
5.  Test repository changes with a disposable/custom `.repo` file when
    possible.
6.  Run the syntax check:

``` bash
python3 -m py_compile package.py
```

7.  Submit a pull request describing what changed and why.

For repository-management changes, be especially careful with code that
writes to `/etc/yum.repos.d/`.

## Reporting bugs

When reporting a problem, useful information includes:

-   Fedora version
-   DNF version
-   Python version
-   Basic Repo version
-   terminal output
-   steps to reproduce the issue

Useful commands:

``` bash
cat /etc/fedora-release
dnf --version
python3 --version
```

Do not publish passwords, authentication tokens, private repository
credentials, or other secrets in bug reports.

## Philosophy

Basic Repo aims to make Fedora package and repository management easier
to inspect without hiding the tools underneath it.

DNF and RPM remain the package-management backend. Basic Repo provides a
graphical layer around those tools and keeps potentially destructive
repository actions under user control.

## License

Basic Repo is intended to be open source under the **MIT License**.

Add a `LICENSE` file containing the MIT License before publishing a
release. Replace the copyright holder and year with the appropriate
project information.

------------------------------------------------------------------------

**Basic Repo** --- a simpler graphical view of Fedora packages and
repositories.
