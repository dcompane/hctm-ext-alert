ctm run alerts::close true
ctm run alerts:stream:temnplat::set -f field_names.json
ctm run alerts:listener:environment::set $(ctm env show |grep -i current |awk '{print $3}')
ctm run alerts::status
ctm run alerts::open