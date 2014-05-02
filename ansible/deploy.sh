ansible-playbook -vvvv -i playbooks/hosts playbooks/setup_server.yml playbooks/deploy.yml --private-key=~/.ssh/dc --ask-vault-pass
