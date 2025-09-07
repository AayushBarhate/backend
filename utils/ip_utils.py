from flask import request
import ipaddress

def get_client_ip():
    """
    Get the real client IP address, considering various proxy headers.
    Returns the most trustworthy IP address available.
    """
    # With ProxyFix configured, request.remote_addr should contain the real client IP
    # But we'll implement a fallback strategy for additional reliability
    
    # First, try the remote_addr (should be set correctly by ProxyFix)
    if request.remote_addr:
        try:
            # Validate IP address
            ipaddress.ip_address(request.remote_addr)
            # Skip local/private IPs if we have better options
            if not _is_private_ip(request.remote_addr):
                return request.remote_addr
        except (ipaddress.AddressValueError, ValueError):
            pass
    
    # Fallback: Check common proxy headers in order of preference
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',    # Cloudflare Enterprise
        'X-Forwarded'
    ]
    
    for header in headers_to_check:
        header_value = request.headers.get(header)
        if header_value:
            # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
            # Take the first (leftmost) IP as it's usually the original client
            ip = header_value.split(',')[0].strip()
            
            try:
                # Validate IP address
                ipaddress.ip_address(ip)
                # Prefer public IPs over private ones
                if not _is_private_ip(ip):
                    return ip
            except (ipaddress.AddressValueError, ValueError):
                continue
    
    # Last resort: return remote_addr even if it's private/local
    return request.remote_addr or 'unknown'

def _is_private_ip(ip_str):
    """Check if an IP address is private/local"""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except (ipaddress.AddressValueError, ValueError):
        return False

def get_ip_info(ip_address):
    """Get additional information about an IP address"""
    if not ip_address or ip_address == 'unknown':
        return {'type': 'unknown'}
    
    try:
        ip = ipaddress.ip_address(ip_address)
        
        info = {
            'address': ip_address,
            'version': ip.version,
            'is_private': ip.is_private,
            'is_loopback': ip.is_loopback,
            'is_multicast': ip.is_multicast,
        }
        
        # Determine IP type
        if ip.is_loopback:
            info['type'] = 'loopback'
        elif ip.is_private:
            info['type'] = 'private'
        elif ip.is_multicast:
            info['type'] = 'multicast'
        else:
            info['type'] = 'public'
            
        return info
        
    except (ipaddress.AddressValueError, ValueError):
        return {
            'address': ip_address,
            'type': 'invalid'
        }