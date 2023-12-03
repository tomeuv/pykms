#!/bin/sh

INCLUDE_PATH="/usr/include"
INCLUDES="
	${INCLUDE_PATH}/drm/drm.h
	${INCLUDE_PATH}/drm/drm_mode.h
	${INCLUDE_PATH}/drm/drm_fourcc.h
"

OUT=kms/kernel/kms.py

ctypesgen  --no-embed-preamble -I${INCLUDE_PATH} -D__volatile__= -D__signed__= -U__SIZEOF_INT128__ -o ${OUT} ${INCLUDES}

# Fix _IOC by using ord(type)
sed --in-place s#"return ((((dir << _IOC_DIRSHIFT) | (type << _IOC_TYPESHIFT)) | (nr << _IOC_NRSHIFT)) | (size << _IOC_SIZESHIFT))"#"return ((((dir << _IOC_DIRSHIFT) | (ord(type) << _IOC_TYPESHIFT)) | (nr << _IOC_NRSHIFT)) | (size << _IOC_SIZESHIFT))"# ${OUT}
