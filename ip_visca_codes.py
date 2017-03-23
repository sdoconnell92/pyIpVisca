# inq = "0110"
# command = "0100"
# visca_reply = "0111"
# visca_device_setting_command = "0120"
# control_comand = "0200"
# control_reply = "0201"

clear_seq = "01000000ffffffff".decode('hex')

# go
power_on = "01000006000000008101040002ff".decode('hex')
power_off = "01000006000000008101040003ff".decode('hex')
go_home = "010000050000000081010604ff".decode('hex')
go_preset1 = "01000007000000008101043F0200ff".decode('hex')
go_preset2 = "01000007000000008101043F0201ff".decode('hex')
go_preset3 = "01000007000000008101043F0202ff".decode('hex')
go_preset4 = "01000007000000008101043F0203ff".decode('hex')

# inquiry
power_inq_com = "011000050000000081090400ff".decode('hex')

# visca replies
vrep_power_on = "0111000400000000905002ff".decode('hex')
vrep_power_off = "0111000400000000905003ff".decode('hex')
