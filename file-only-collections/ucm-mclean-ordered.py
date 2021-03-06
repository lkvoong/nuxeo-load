#!/usr/bin/env python
import sys, os, shutil, subprocess
import pprint

""" Batch load UCM McLean sub-components with workaround so that they appear in Nuxeo in lexical order. """

content_dir = "/apps/content/new_path/UCM/McLean/"
collection_name = "McLean"
temp_dir = os.path.join("/apps/nuxeo/code/nuxeo-load/file-only-collections/temp-for-loading/", collection_name)
target_base_path = os.path.join("/asset-library/UCM", collection_name)

pp = pprint.PrettyPrinter()

def main(argv=None):
    # create temp collection folder
    _mkdir(temp_dir)
    pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type Organization".format(temp_dir, "/asset-library/UCM")
    print pifolder_cmd
    subprocess.call(pifolder_cmd, shell=True)

    # iterate through directories and load objects
    subdirs = [dirs for root, dirs, files in os.walk(content_dir)][0]
    for subdir in subdirs:
        # complex
        if subdir == "complex":
            subdir_fullpath = os.path.join(content_dir, subdir)
            object_dirs = [dirs for root, dirs, files in os.walk(subdir_fullpath)][0]
            for object_dir in object_dirs:
                object_dir_fullpath = os.path.join(subdir_fullpath, object_dir)
                #print object_dir_fullpath
                load_complex_dir(object_dir_fullpath)
        # do a simple load
        else:
            object_dir_fullpath = os.path.join(content_dir, subdir)
            pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --skip_root_folder_creation --folderish_type SampleCustomPicture".format(object_dir_fullpath, target_base_path)
            print pifolder_cmd
            subprocess.call(pifolder_cmd, shell=True)

    # delete the temp collection folder 
    shutil.rmtree(temp_dir)

def load_complex_dir(content_dir):
    folder = os.path.basename(content_dir)
    input_path = os.path.join(temp_dir, folder)
    _mkdir(input_path)
    target_folder = os.path.join(target_base_path, folder)
    components = [files for root, dirs, files in os.walk(content_dir)][0]
    #components = [f for f in files if f.endswith('.tif')]
    components = sorted(components)
    count = 0
    for component in components: 

        if count == 0:
            pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type SampleCustomPicture".format(input_path, target_base_path)
        else:
            pifolder_cmd = "pifolder --leaf_type SampleCustomPicture --input_path {} --target_path {} --folderish_type SampleCustomPicture --skip_root_folder_creation".format(input_path, target_folder)

        print "\n", pifolder_cmd

        copy_from = os.path.join(content_dir, component)
        copy_to = os.path.join(input_path, component)
        print copy_from, copy_to
        shutil.copy(copy_from, copy_to)

        subprocess.call(pifolder_cmd, shell=True)

        os.remove(copy_to)

        count = count + 1


# http://code.activestate.com/recipes/82465-a-friendly-mkdir/
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)



if __name__ == "__main__":
    sys.exit(main())
