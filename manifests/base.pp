class mongodb {
  $service_name = 'mongodb'

  package { 'mongodb':
    ensure => installed,
  }
  
  service { 'mongodb':
    name      => $service_name,
    ensure    => stopped,
    enable    => false,
  }
  
}

include mongodb