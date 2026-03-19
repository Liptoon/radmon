#!/opt/radmon/venv/bin/python3
import time
import sys
import argparse
import tty
import termios
import select
from radiacode import RadiaCode

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def is_q_pressed():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1).lower() == 'q'
    return False

def interactive_mac_input():
    print("Enter Radiacode MAC:")
    mac = ""
    allowed_chars = "0123456789ABCDEF"
    while len(mac) < 17:
        sys.stdout.write(f"\rMAC: {mac.ljust(17, '_')}")
        sys.stdout.flush()
        try:
            ch = get_char().upper()
            if ch == '\x03' or ch == 'Q':
                print("\nAborted.")
                sys.exit(0)
            if ch == '\x7f' or ch == '\x08':
                if len(mac) > 0:
                    mac = mac[:-1]
                    if len(mac) > 0 and mac[-1] == ':': mac = mac[:-1]
                continue
            if ch in allowed_chars:
                mac += ch
                if len(mac) in [2, 5, 8, 11, 14]: mac += ":"
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(0)
    print(f"\rMAC: {mac} [OK]")
    return mac

def main():
    parser = argparse.ArgumentParser(description='Radmon: Radiacode 102 Monitor')
    parser.add_argument('-m', '--mac', type=str, help='MAC Adress of the Radiacode device')
    parser.add_argument('-i', '--interval', type=int, default=3, help='Averaging interval (s)')
    parser.add_argument('-r', '--runonce', action='store_true', help='Single reading mode (prints one line and exits)')
    args = parser.parse_args()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        bluetooth_mac = args.mac
        if not bluetooth_mac:
            bluetooth_mac = interactive_mac_input()

        if not args.runonce:
            print(f"[*] Connecting to {bluetooth_mac}...")
        
        rc = RadiaCode(bluetooth_mac=bluetooth_mac)
        
        cps_buffer, dose_buffer = [], []
        last_valid_err = 100.0
        last_temp = 0.0
        start_time = time.time()
        header_printed = False

        if not args.runonce:
            print(f"[OK] Connected to: {rc.serial_number()}")
            print(f"[!] Exit: 'q' or Ctrl+C")
            tty.setcbreak(sys.stdin.fileno())

        while True:
            if not args.runonce and is_q_pressed():
                sys.stdout.write("\n")
                break

            records = rc.data_buf()
            for record in records:
                # Pobieranie danych systemowych (temperatura)
                if hasattr(record, 'charge_level'):
                    last_temp = record.temperature
                    if not args.runonce:
                        prefix = "\n" if header_printed else ""
                        sys.stdout.write(f"{prefix}[SYS] Bat: {record.charge_level}% | Temp: {last_temp:.1f}°C\n")
                        if header_printed:
                            header_printed = False 

                # Pobieranie danych radiacyjnych
                if hasattr(record, 'count_rate'):
                    cps_buffer.append(record.count_rate)
                    dose_buffer.append(getattr(record, 'dose_rate', 0.0) * 10000.0)
                    current_err = getattr(record, 'dose_rate_err', 100.0)
                    if 0.1 < current_err < 100.0: last_valid_err = current_err

            current_time = time.time()
            if current_time - start_time >= args.interval:
                if cps_buffer:
                    avg_cps = sum(cps_buffer) / len(cps_buffer)
                    avg_cpm = avg_cps * 60
                    avg_usv = sum(dose_buffer) / len(dose_buffer)
                    avg_ur = avg_usv * 100.0
                    ts = time.strftime('%H:%M:%S')
                    
                    if args.runonce:
                        # Tryb runonce:
                        print(f"t={ts}  HT={avg_usv:.4f}µSv/h  HT={avg_ur:.2f}µR/h  CPS={avg_cps:.1f}  CPM={int(avg_cpm)}  Err={last_valid_err:.1f}% Temp={last_temp:.1f}°C")
                        return 
                    else:
                        # Tryb Live: tabela 
                        if not header_printed:
                            h_text = f"{'Time':<10} | {'CPS (CPM)':>12} | {f'µSv/h ({args.interval}s)':>12} | {f'µR/h ({args.interval}s)':>12} | {'Err +/-':>6}"
                            h_line = "-" * len(h_text)
                            sys.stdout.write(f"{h_line}\n{h_text}\n{h_line}\n")
                            header_printed = True

                        cps_cpm_str = f"{avg_cps:>5.1f} ({int(avg_cpm):>4})"
                        output = f"{ts:<10} | {cps_cpm_str:>12} | {avg_usv:>12.4f} | {avg_ur:>12.2f} | {last_valid_err:>5.1f}%"
                        sys.stdout.write(f"\r{output}")
                        sys.stdout.flush()
                        
                        cps_buffer, dose_buffer = [], []
                        start_time = current_time

            time.sleep(0.1)

    except KeyboardInterrupt:
        if not args.runonce:
            sys.stdout.write("\n")
            print("[INFO] Aborted (Ctrl+C).")
    except Exception as e:
        print(f"\n[ERR] {e}")
    finally:
        if not args.runonce:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()