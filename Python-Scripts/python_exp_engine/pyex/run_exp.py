#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from Queue import Queue

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory


def render_expect_file():
    pass


def run_expect():
    pass


def extract_hosts(inventory, section):
    if not isinstance(inventory, Inventory):
        return list()

    # get root group
    group = inventory.groups.get("all")
    groups = Queue()
    groups.put(group)
    hosts = list()
    while not groups.empty():
        g = groups.get()
        # iterate all groups by wide first method to add selected section hosts
        if g.name == section:
            # find the target groups, iterate all groups to get all hosts
            target_groups = Queue()
            target_groups.put(g)
            while not target_groups.empty():
                tg = target_groups.get()
                for host in tg.hosts:
                    host_data = dict()
                    host_data['name'] = host.name
                    host_data['address'] = host.address
                    host_data['vars'] = dict()
                    host_data['vars'].update(host.vars)
                    host_data['vars'].update(tg.vars)

                    # interate all its group and all its parent group to get variable
                    # this method has low performance, however, it is fast enough for
                    # there will not be too many hosts
                    for pg in tg.parent_groups:
                        host_data['vars'].update(pg.vars)

                    hosts.append(host_data)
                for sub_tg in tg.child_groups:
                    target_groups.put(sub_tg)
            return hosts
        else:
            for sub_group in g.child_group:
                groups.put(sub_group)

    # if the section not exist, return empty array
    return hosts


def main(host="hosts", section="all", template=None):
    variable_manager = VariableManager()
    loader = DataLoader()
    inventory = Inventory(
        loader=loader,
        variable_manager=variable_manager,
        host_list=host
    )

    host_list = extract_hosts(inventory, section)

    for h in host_list:
        print h

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python Expect Template Engine')
    parser.add_argument("-i",
                        "--inventory",
                        dest="hosts",
                        help="server list file",
                        const="hosts",
                        default="hosts",
                        action="store_const"
                        )
    parser.add_argument("-g",
                        "--group",
                        dest="group",
                        help="section for server list in server list file to choose servers",
                        const="all",
                        default="all",
                        action="store_const"
                        )
    parser.add_argument("-s",
                        "--server",
                        dest="server",
                        help="define one server to run",
                        const="None",
                        action="store_const"
                        )
    parser.add_argument("-t",
                        "--template",
                        dest="template",
                        help="jinjia template file to generate expect commands",
                        const="template/main.j2",
                        default="tempate/main.j2",
                        action="store_const")
    args = parser.parse_args()
    main(args.hosts, args.group, args.template)
