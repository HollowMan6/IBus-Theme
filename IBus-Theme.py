#!/usr/bin/python3
# vim: set fileencoding=utf-8 :
# vim: set et ts=4 sw=4:
'''
  IBus Theme Tools
  Author:  Hollow Man <hollowman@hollowman.ml>

  Copyright © 2021 Hollow Man(@HollowMan6). All rights reserved.

  This document is free software; you can redistribute it and/or modify it under the terms of the GNU General
  Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option)
  any later version.
'''
import re
import tinycss2
from gi.repository import GLib
import os

import gettext
APP_NAME = "IBus-Theme"
LOCALE_DIR = os.path.abspath("locale")
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

EXTENSION_URL = "https://extensions.gnome.org/extension/4112/customize-ibus/"
SOURCE_CODE_URL = "https://github.com/HollowMan6/IBus-Theme"


def getThemePathList():
    pathList = []
    pathList.append(os.path.join(GLib.get_home_dir(), ".themes"))
    pathList.append(os.path.join(GLib.get_user_data_dir(), "themes"))
    pathList.extend(list(map(lambda x: os.path.join(
        x, "themes"), GLib.get_system_data_dirs())))
    return pathList

# For Non-GNOME Desktop


def getAvailableGTKTheme():
    themeNameList = []
    pathList = getThemePathList()
    GTKVersionList = ["3.0", "3.20", "4.0"]
    for path in pathList:
        if os.path.isdir(path):
            files = os.listdir(path)
            for p in files:
                if os.path.isdir(os.path.join(path, p)):
                    for version in GTKVersionList:
                        if os.path.isfile(os.path.join(path, p, "gtk-"+version, "gtk.css")):
                            themeNameList.append(p)
                            break
    return themeNameList


def addStartup(themeName):
    startupDir = os.path.join(GLib.get_user_config_dir(), "autostart")
    if not os.path.exists(startupDir):
        os.makedirs(startupDir)
    with open(os.path.join(startupDir, "org.hollowman.ibus-gtk-theme-customize.desktop"), "w") as f:
        content = "[Desktop Entry]\n" + \
            "Name=ibus-gtk-theme-customize\n" + \
            "Name[zh_CN]=ibus-gtk-主题自定义\n" + \
            "GenericName=Customize IBus Theme\n" + \
            "GenericName[zh_CN]=自定义IBus 主题\n" + \
            "Icon=ibus\n" + \
            "Exec=bash -c 'pkill ibus-daemon;GTK_THEME=" + themeName + " ibus-daemon -dx &'\n" + \
            "Comment=Applying user selected GTK theme for IBus\n" + \
            "Comment[zh_CN]=应用用户选择的IBus GTK主题\n" + \
            "Terminal=false\n" + \
            "Type=Application\n" + \
            "Categories=System;Settings;IBus;\n" + \
            "StartupNotify=false\n"
        f.write(content)


def changeGTKTheme():
    themeNameList = getAvailableGTKTheme()
    themeNameList.sort()
    count = 1
    while True:
        print(_("Please select a GTK theme to apply for IBus:"))
        for themeName in themeNameList:
            print("["+str(count)+"]\t"+themeName)
            count += 1
        print("[q]\t"+_("Exit"))
        selection = input(_("(Empty to exit): "))
        if selection == "q" or not selection:
            print(_("Goodbye!"))
            exit(0)
        elif selection.isdigit() and int(selection) < count and int(selection) > 0:
            while True:
                print(_("Please select a theme mode (Not guaranteed to work):"))
                print("[0]\t"+_("Default"))
                print("[1]\t"+_("Light"))
                print("[2]\t"+_("Dark"))
                print("[q]\t"+_("Exit"))
                modeSelection = input(_("(Empty to be default): "))
                if modeSelection == "q":
                    print(_("Goodbye!"))
                    exit(0)
                elif modeSelection.isdigit() and int(modeSelection) >= 0 and int(modeSelection) <= 2 or not modeSelection:
                    mode = ""
                    if not modeSelection or modeSelection == "0":
                        pass
                    elif modeSelection == "1":
                        mode = ":light"
                    elif modeSelection == "2":
                        mode = ":dark"
                    os.system("pkill ibus-daemon")
                    os.system("GTK_THEME=" +
                              themeNameList[int(selection)-1] + mode + " ibus-daemon -dx &")
                    addStartup(themeNameList[int(selection)-1] + mode)
                    print(_("Done! Goodbye!"))
                    exit(0)
                else:
                    print(_("Error: Wrong selection!\n"))
        else:
            print(_("Error: Wrong selection!\n"))
            count = 1

# For GNOME Desktop


def getAvailableGNOMETheme():
    themeList = []
    pathList = getThemePathList()
    for path in pathList:
        if os.path.isdir(path):
            files = os.listdir(path)
            for p in files:
                if os.path.isdir(os.path.join(path, p)):
                    if os.path.isfile(os.path.join(path, p, "gnome-shell", "gnome-shell.css")):
                        themeList.append(os.path.join(
                            path, p, "gnome-shell", "gnome-shell.css"))
    pathList = list(map(lambda x: os.path.join(
        x, "gnome-shell", "theme"), GLib.get_system_data_dirs()))
    for path in pathList:
        if os.path.isdir(path):
            files = os.listdir(path)
            for p in files:
                if os.path.isfile(os.path.join(path, p)) and os.path.splitext(os.path.join(path, p))[-1] == ".css":
                    if os.path.isfile(os.path.join(path, p)):
                        themeList.append(os.path.join(path, p))
    return themeList


def RMUnrelatedStyleClass(string):
    classList = string.split(",")
    newClassList = []
    for className in classList:
        if ".candidate-" in className:
            newClassList.append(className)
    return ",".join(newClassList)


def exportIBusGNOMEThemeCSS(styleSheet, recursive=False):
    newCSS = _("/*\n Generated by IBus Theme Tools\n") + \
        _(" Tool Author:") + " Hollow Man <hollowman@hollowman.ml>\n" + \
        _(" Tool Source Code:") + " " + SOURCE_CODE_URL + "\n" + \
        _(" Tool Licence:") + " GPLv3\n" + \
        _(" CSS Source File: ") + styleSheet + "\n" + \
        _("\n Recommend to use Customize IBus GNOME Shell Extension:") + "\n " + EXTENSION_URL + "\n" + \
        _(" to change IBus theme by selecting this file.\n") + \
        _("\n If you make any changes to this content after applying this file in above extension, \n") + \
        _(" please press 'Alt + F2' and then 'r' or re-login to reload the GNOME-Shell to make the changes take effect.\n") + \
        "*/\n\n"
    if recursive:
        newCSS = _("/*\n Imported from CSS Source File: ") + \
            styleSheet + "\n*/\n\n"
    # For fix candidate color
    globalColor = ""
    boxContent = ""
    popupContent = ""

    # For fix black border at pointer when system theme is black
    popupBoxpointerContent = ""

    # For unify system page button and IBus style page button
    pageButtonContent = ""

    with open(styleSheet) as f:
        tokenList = tinycss2.parse_stylesheet(
            f.read(), skip_comments=True, skip_whitespace=True)
        for token in tokenList:
            if token.type == "qualified-rule":
                classStr = tinycss2.serialize(token.prelude)
                cleanClassList = list(
                    map(lambda x: x.strip(), classStr.split(",")))
                # For IBus candidate page button
                if ".button" in classStr:
                    newCleanClassList = []
                    for cleanClass in cleanClassList:
                        if cleanClass == ".button":
                            pageButtonContent += tinycss2.serialize(
                                token.content)
                        elif cleanClass.startswith(".button"):
                            newCleanClassList.append(cleanClass.replace(
                                ".button", ".candidate-page-button"))
                        else:
                            newCleanClassList.append(cleanClass)
                    cleanClassList = newCleanClassList
                    classStr = ", ".join(cleanClassList) + " "

                # For get candidate color
                if ".popup-menu" in cleanClassList:
                    contentStr = tinycss2.serialize(token.content)
                    color = re.findall(r' color:(.+?);', contentStr)
                    if color:
                        globalColor = color[0]
                    else:
                        color = re.findall(r'\ncolor:(.+?);', contentStr)
                        if color:
                            globalColor = color[0]

                # For check if need to fix candidate color
                if ".candidate-box" in cleanClassList:
                    contentStr = tinycss2.serialize(token.content)
                    if not (" color:" in contentStr or "\ncolor:" in contentStr):
                        boxContent = contentStr
                        cleanClassList.remove(".candidate-box")
                        classStr = ", ".join(cleanClassList) + " "

                if ".candidate-popup-content" in cleanClassList:
                    contentStr = tinycss2.serialize(token.content)
                    if not (" color:" in contentStr or "\ncolor:" in contentStr):
                        popupContent = contentStr
                        cleanClassList.remove(".candidate-popup-content")
                        classStr = ", ".join(cleanClassList) + " "

                # For check if need to fix border at pointer
                if ".candidate-popup-boxpointer" in cleanClassList:
                    contentStr = tinycss2.serialize(token.content)
                    if not (" border-image:" in contentStr or "\nborder-image:" in contentStr):
                        popupBoxpointerContent = contentStr
                        cleanClassList.remove(".candidate-popup-boxpointer")
                        classStr = ", ".join(cleanClassList) + " "

                if ".candidate-page-button" in cleanClassList:
                    contentStr = tinycss2.serialize(token.content)
                    pageButtonContent += _("  /* IBus style page button */") + \
                        contentStr
                    cleanClassList.remove(".candidate-page-button")
                    classStr = ", ".join(cleanClassList) + " "

                if not ".candidate-" in classStr:
                    continue

                classStr = RMUnrelatedStyleClass(classStr)
                contentStr = tinycss2.serialize(token.content)
                contentStr = contentStr.replace(
                    "assets/", os.path.split(styleSheet)[0] + "/assets/")
                newCSS += classStr + "{" + contentStr + "}\n\n"
            elif token.type == 'at-rule' and token.lower_at_keyword == 'import':
                for importToken in token.prelude:
                    if importToken.type == "function" and importToken.name == "url":
                        url = tinycss2.serialize(
                            importToken.arguments).strip("'").strip('"')
                        if not os.path.isfile(url):
                            url = os.path.join(
                                os.path.split(styleSheet)[0], url)
                            if not os.path.isfile(url):
                                continue
                        newCSS += exportIBusGNOMEThemeCSS(
                            url, True) + _("\n/* EOF */\n")
                        break

    # Fix candidate color
    colorString = _("  /* Fix candidate color */") + \
        "\n  color:" + globalColor + ";\n"
    if boxContent:
        newCSS += ".candidate-box {" + boxContent + colorString + "}\n\n"
    if popupContent and globalColor:
        newCSS += ".candidate-popup-content {" + \
            popupContent + colorString + "}\n\n"

    # Fix black border at pointer when system theme is black
    if popupBoxpointerContent:
        newCSS += ".candidate-popup-boxpointer {" + popupBoxpointerContent + _("  /* Fix black border at pointer when system theme is black */\n") + \
            "  border-image: none;\n}\n\n"

    # Unify system page button and IBus style page button
    if pageButtonContent:
        newCSS += _("/* Unify system page button and IBus style page button */\n")
        newCSS += ".candidate-page-button {" + pageButtonContent + "}\n"

    return newCSS


def exportIBusTheme():
    themeList = getAvailableGNOMETheme()
    themeList.sort()
    count = 1
    while True:
        print(_("Please select a GNOME theme to extract style sheet for IBus:"))
        for theme in themeList:
            print("["+str(count)+"]\t"+theme)
            count += 1
        print("[q]\t"+_("Exit"))
        selection = input(_("(Empty to exit): "))
        if selection == "q" or not selection:
            print(_("Goodbye!"))
            exit(0)
        elif selection.isdigit() and int(selection) < count and int(selection) > 0:
            print(_("Please enter the path to store generated stylesheet:"))
            path = input(
                _("(Empty to be 'exportedIBusTheme.css' in current directory): "))
            if not path:
                path = "exportedIBusTheme.css"
            newCSS = exportIBusGNOMEThemeCSS(themeList[int(selection)-1])
            with open(path, "w") as f:
                f.write(newCSS)
            print(
                _("\nNow you can use Customize IBus GNOME Shell Extension:\n") + EXTENSION_URL)
            print(_("to change IBus theme by selecting the extracted stylesheet."))
            print(_("\nIf you make any changes to the extracted stylesheet after applying the file in above extension,"))
            print(_("please press 'Alt + F2' and then 'r' or re-login to reload the GNOME-Shell to make the changes take effect."))
            print(_("\nDone! Goodbye!"))
            exit(0)
        else:
            print(_("Error: Wrong selection!\n"))
            count = 1


if __name__ == "__main__":
    try:
        desktopEnv = os.environ["XDG_CURRENT_DESKTOP"].split(":")
    except Exception:
        print(_("Error: Not in Linux!"))
        exit(1)
    if "GNOME" in desktopEnv:
        exportIBusTheme()
    else:
        changeGTKTheme()
