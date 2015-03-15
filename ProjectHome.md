# Trash - command-line utility to manage GNOME trash can #

## Basic operations ##

```
# trash some files
```

moves some files into the trash can.

```
# trash -rf some dirs
```

forcely moves some directories into the trash can.
"-r" and "-f" options are same with GNU rm, so you can alias trash as rm.

```
# alias rm=trash
```

You can see the list of trashes by simply type "rm".

```
# rm
```

A regular expression and timestamp queries are also available with -e and -H options.

```
# rm -e test
    -> queries trashes includes string 'test' in the filename.
# rm -H 72
    -> queries trashes removed before 72 hours.
```

-D option REALLY deletes trashes from the trash can. It's irreversible operation.

```
# rm -H 72 -D
    -> deletes trashes removed before 72 hours.
```

To undelete the most recent trash from the trash can;

```
# rm -U
```

Undeleted file(s) will be placed in current working directory.

You can specify the trash file by its list number. The number starts with 0, trash command shows full list of trashes with the number (simply type "rm").
```
# rm
# rm -U 3
```