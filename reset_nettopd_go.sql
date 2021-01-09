
SET foreign_key_checks = 0;
truncate table topo_position;
truncate table topo_phyvirt;
truncate table nfvapp_inuse;
truncate table nfvapp_basic;
truncate table topo_config;
update server_physical_interfaces set used=0;
SET foreign_key_checks = 1;
