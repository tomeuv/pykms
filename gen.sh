#!/bin/sh

INCLUDE_PATH="/usr/include"
INCLUDES="
	${INCLUDE_PATH}/drm/drm.h
	${INCLUDE_PATH}/drm/drm_mode.h
	${INCLUDE_PATH}/drm/drm_fourcc.h
"

OUT=kms/uapi/kms.py

#CTYPESGEN=ctypesgen
CTYPESGEN=/home/tomba/work/ctypesgen/run.py

CTYPESGEN_OPTS="--no-embed-preamble --no-macro-try-except --no-source-comments -D__volatile__= -D__signed__= -U__SIZEOF_INT128__"

${CTYPESGEN} ${CTYPESGEN_OPTS} -I${INCLUDE_PATH} -o ${OUT} ${INCLUDES}

# Fix _IOC by using ord(type)
sed --in-place s#"return ((((dir << _IOC_DIRSHIFT) | (type << _IOC_TYPESHIFT)) | (nr << _IOC_NRSHIFT)) | (size << _IOC_SIZESHIFT))"#"return ((((dir << _IOC_DIRSHIFT) | (ord(type) << _IOC_TYPESHIFT)) | (nr << _IOC_NRSHIFT)) | (size << _IOC_SIZESHIFT))"# ${OUT}

# Add pylint ignore comment
sed --in-place s/"^def POINTER(obj):"/"def POINTER(obj): # pylint: disable=function-redefined:"/ kms/uapi/ctypes_preamble.py
