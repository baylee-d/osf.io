from website.notifications.emails import compile_subscriptions
from website.notifications import utils, constants


def get_file_subs_from_folder(addon, user, kind, path, name):
    """Find the file tree under a specified folder."""
    folder = dict(kind=kind, path=path, name=name)
    file_tree = addon._get_file_tree(filenode=folder, user=user, version='latest-published')
    files = []
    list_of_files(file_tree, files)
    return files


def list_of_files(file_object, files):
    """Recursively make a flat list of files in a directory."""
    if file_object['kind'] == 'file':
        files.append(file_object['path'])
    else:
        for child in file_object['children']:
            list_of_files(child, files)


def get_file_guid(node, provider, path):
    """Use node, provider, and waterbutler path to find guid."""
    path = path if path.startswith('/') else '/' + path
    addon = node.get_addon(provider)
    guid, created = addon.find_or_create_file_guid(path)
    return guid


def compile_user_lists(files, user, source_node, node):
    """Take multiple file ids and compiles them.

    :param files: List of WaterButler paths
    :param user: User who initiated action/event
    :param source_node: Node instance from
    :param node: Node instance to
    :return: move, warn, and remove dicts
    """
    # initialise subscription dictionaries
    move = {key: [] for key in constants.NOTIFICATION_TYPES}
    warn = {key: [] for key in constants.NOTIFICATION_TYPES}
    remove = {key: [] for key in constants.NOTIFICATION_TYPES}
    # get the node subscription
    if len(files) == 0:
        move, warn, remove = categorize_users(
            user, 'file_updated', source_node, 'file_updated', node
        )
    # iterate through file subscriptions
    for file_path in files:
        path = file_path.strip('/')
        t_move, t_warn, t_remove = categorize_users(
            user, path + '_file_updated', source_node,
            path + '_file_updated', node
        )
        # Add file subs to overall list of subscriptions
        for notification in constants.NOTIFICATION_TYPES:
            move[notification] = list(set(move[notification]).union(set(t_move[notification])))
            warn[notification] = list(set(warn[notification]).union(set(t_warn[notification])))
            remove[notification] = list(set(remove[notification]).union(set(t_remove[notification])))
    return move, warn, remove


def categorize_users(user, source_event, source_node, event, node):
    """Categorize users from a file subscription into three categories.

    Puts users in one of three bins: Those that are moved, those that
     need warned, those that are removed.
    Calls move_subscription in order to move the sub and get users w/o permissions
    :param user: User instance who started the event
    :param source_event: <guid>_event_name
    :param source_node: node from where the event happened
    :param event: new guid event name
    :param node: node where event ends up
    :return: Moved, to be warned, and removed users.
    """
    remove = utils.users_to_remove(source_event, source_node, node)
    source_node_subs = compile_subscriptions(source_node, utils.find_subscription_type(source_event))
    new_subs = compile_subscriptions(node, utils.find_subscription_type(source_event), event)

    # Moves users into the warn bucket or the move bucket
    move = subscriptions_users_union(source_node_subs, new_subs)
    warn = subscriptions_users_difference(source_node_subs, new_subs)

    # Removes users without permissions
    warn, remove = subscriptions_node_permissions(node, warn, remove)

    # Remove duplicates
    warn = subscriptions_users_remove_duplicates(warn, new_subs, remove_same=False)
    move = subscriptions_users_remove_duplicates(move, new_subs, remove_same=False)

    # Remove duplicates between move and warn; and move and remove
    move = subscriptions_users_remove_duplicates(move, warn, remove_same=True)
    move = subscriptions_users_remove_duplicates(move, remove, remove_same=True)

    for notifications in constants.NOTIFICATION_TYPES:
        # Remove the user who started this whole thing.
        user_id = user._id
        if user_id in warn[notifications]:
            warn[notifications].remove(user_id)
        if user_id in move[notifications]:
            move[notifications].remove(user_id)
        if user_id in remove[notifications]:
            remove[notifications].remove(user_id)

    return move, warn, remove


def subscriptions_node_permissions(node, warn_subscription, remove_subscription):
    for notification in constants.NOTIFICATION_TYPES:
        subbed, removed = utils.separate_users(node, warn_subscription[notification])
        warn_subscription[notification] = subbed
        remove_subscription[notification].extend(removed)
        remove_subscription[notification] = list(set(remove_subscription[notification]))
    return warn_subscription, remove_subscription


def subscriptions_users_union(emails_1, emails_2):
    return {
        notification:
            list(
                set(emails_1[notification]).union(set(emails_2[notification]))
            )
        for notification in constants.NOTIFICATION_TYPES.keys()
    }


def subscriptions_users_difference(emails_1, emails_2):
    return {
        notification:
            list(
                set(emails_1[notification]).difference(set(emails_2[notification]))
            )
        for notification in constants.NOTIFICATION_TYPES.keys()
    }


def subscriptions_users_remove_duplicates(emails_1, emails_2, remove_same=False):
    emails_list = dict(emails_1)
    for notifications in constants.NOTIFICATION_TYPES:
        for nt in constants.NOTIFICATION_TYPES:
            if nt == 'none' or not remove_same and nt == notifications:
                continue
            emails_list[notifications] = list(
                set(emails_list[notifications]).difference(set(emails_2[nt]))
            )
    return emails_list
