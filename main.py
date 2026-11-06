#!/user/bin/env python3
#
# MagiskMorphida build process
#
# 1. Checks if project has a tag that matches the latest Morphida tag
#    (Morphida tags look like 17.25.2-r11b9cbe3; the prefix is the Frida version,
#    the -r suffix is a per-build morph identifier)
#    Yes -> continue
#    No  -> must tag
# 2. Checks if FORCE_RELEASE environment variable is set (GitHub Actions)
#    Yes -> must tag
#    No  -> continue
# If tagging, writes new tag to 'NEW_TAG.txt' and builds
# Otherwise, does nothing and builds with placeholder tag
# 3. Deployment will execute only if 'NEW_TAG.txt' is present
#
# NOTE: Requires git
#

import build
import util
import os


def main():
    last_morphida_tag = util.get_last_morphida_tag()
    last_project_tag = util.get_last_project_tag()

    force_release = os.getenv('FORCE_RELEASE', 'false').lower() == 'true'
    # strip any force suffix (-2, -3, ...) before comparing with upstream
    last_upstream_tag = util.strip_force_suffix(last_project_tag)
    needs_update = last_upstream_tag != last_morphida_tag

    if needs_update or force_release:
        if needs_update:
            new_project_tag = last_morphida_tag
            print(f"Update needed to {new_project_tag}")
            print(f"Reason: Morphida updated from '{last_upstream_tag}' to '{last_morphida_tag}'")
        else:
            new_project_tag = util.get_next_force_tag(last_morphida_tag)
            print(f"Update needed to {new_project_tag}")
            print("Reason: Force release requested via GitHub Actions")

        # for use by deployment
        with open("NEW_TAG.txt", "w") as the_file:
            the_file.write(new_project_tag)
    else:
        new_project_tag = "0"
        print("All good!")

    build.do_build(last_morphida_tag, new_project_tag)


if __name__ == "__main__":
    main()
