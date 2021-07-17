from application.copytools.copytool_parser import CopytoolParser
from exceptions.action_not_supported_exception import ActionNotSupportedException
from worker.action import Action


def determine_copytool(src_storj, target_storj):
    action = determine_action(src_storj, target_storj)
    copytools = CopytoolParser().copytools
    for name, options in copytools.items():
        if supports_action(options['copytool'], action): return {**options, 'action':action.value}
    raise ActionNotSupportedException("No copytool was found, which supports this trasformation.")


def determine_action(src_storage, tgt_storage):
    if src_storage.is_archive and not tgt_storage.is_archive:
        action = Action.EXTRACT_TAR
    elif tgt_storage.is_archive and not src_storage.is_archive:
        action = Action.COMPRESS_TAR
    else:
        action = Action.COPY
    return action

def supports_action(copytool, action):
    i = dict(
        rsync=[Action.COPY],
        tar=[Action.COMPRESS_TAR, Action.EXTRACT_TAR]
    )
    return True if action in i[copytool] else False