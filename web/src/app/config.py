from dataclasses import dataclass


@dataclass
class Config:
    generator_create = 'http://generator:8000/create'
    generator_view = 'http://generator:8000/visualize'
    generator_pavel_create = 'http://11.11.1.111:8080/create'
    generator_pavel_view = 'http://11.11.1.111:8080/visualize'
    ldap_info_group = 'http://11.11.1.111:4569/info/user?login=%s&group=Schedule'
    ldap_info_auth = 'http://11.11.1.111:4569/info/auth?login=%s&password=%s'