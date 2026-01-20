from dataclasses import dataclass


@dataclass
class Config:
    generator_create = 'http://generator:8000/create_schedule'
    generator_view = 'http://generator:8000/visualize_schedule'
    generator_pavel_create = 'http://10.10.1.125:8085/create_schedule'
    generator_pavel_view = 'http://10.10.1.125:8085/visualize_schedule'
    ldap_info_group = 'http://10.10.1.125:4569/info/user?login=%s&group=ScheduleGeneratorAdmins'
    ldap_info_auth = 'http://10.10.1.125:4569/info/auth?login=%s&password=%s'