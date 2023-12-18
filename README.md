# Portage File List Client
This are the client scripts used by Portage File List (PFL) to upload file names of installed Gentoo packages.
PFL allows users to search for files that are not installed on their system and figure out which ebuild they need to install in order to obtain it.

It also provides a tool for searching PFL from CLI (e-file).

## Install
`# emerge app-portage/pfl -av`

## Upload installed packages

### Why?
As Gentoo has a source code based package system you cannot predict the binary files created by a package.
Thus you might have trouble to find the package which provides a specific binary. E.g. the command `brctl` is
provided by the package `net-misc/bridge-utils`. [Try it](https://www.portagefilelist.de/index.php?fs=brctl&unique=1).

### How?
Just execute `pfl` to upload your installed information. It is incremental. To reset, delete: `~/.pfl.info`.
Or use the network-cron useflag which installs a weekly executed cronjob using any cron installation.

There is also a [systemd timer](https://wiki.gentoo.org/wiki/Systemd#Timer_services) available.
It is installed by default but inactive. The timer needs to be activated by hand: `systemctl enable pfl.timer`.
Just make sure to use either of the crons.

#### Specific package only
If there is the need to upload only a specific package atom, provide it with the `-a|--atom` cli option.
Only the specific package atom syntax is currently supported. Like `=media-fonts/fira-code-6.2` and NOT `media-fonts/fira-code`

#### Pretend mode, or just want to know what is uploaded?
Use `-p|--pretend` as a cli option to gather the data and leaving the xml file behind. It prints the location to be
viewed. This option does not set the last updated timestamp but uses it if available.

## CLI Search

The package does provide a cli command `e-file` to execute a search in your terminal.
`$ e-file [-h] [-v] file`

Example: `$ e-file brctl` results in

```
 *  app-shells/bash-completion
        Seen Versions:          2.11
        Portage Versions:       2.11 9999
        Homepage:               https://github.com/scop/bash-completion
        Description:            Programmable Completion for bash
        Matched Files:          /usr/share/bash-completion/completions/brctl/brctl

 *  net-misc/bridge-utils
        Seen Versions:          1.7.1-r1
        Portage Versions:       1.7.1-r1
        Homepage:               http://bridge.sourceforge.net/
        Description:            Tools for configuring the Linux kernel 802.1d Ethernet Bridge
        Matched Files:          /sbin/brctl/brctl
```

It also displays any current installed packages on your system and wildcardsearch:

```
$ e-file apache2ct*
[I] www-servers/apache
        Seen Versions:          2.2.29 2.4.34-r2 2.4.39 2.4.55-r1 2.4.57 2.4.57-r1
        Portage Versions:       2.4.57 2.4.57-r1
        Installed Versions:     2.4.57(Fri Jun 23 06:43:37 2023)
        Homepage:               https://httpd.apache.org/
        Description:            The Apache Web Server
        Matched Files:          /usr/sbin/apache2ctl/apache2ctl

 *  app-shells/bash-completion
        Seen Versions:          2.11
        Portage Versions:       2.11 9999
        Homepage:               https://github.com/scop/bash-completion
        Description:            Programmable Completion for bash
        Matched Files:          /usr/share/bash-completion/completions/apache2ctl/apache2ctl
```

The e-file does only provide searching for packages with a given filename. More options are available with the browser search.

## Browser Search

Searching through the user provided uploads for a package, package itself and categories can be done [at the website itself](https://www.portagefilelist.de/).
