# Direkter GPIO Zugriff über Memory-Map

Neben der universellen Methode über `/sys/class/gpio` besteht die Möglichkeit, über ein Memory-Map direkt auf die GPIOs und die angeschlossene Peripherie zuzugreifen.
Dafür übersetzt der Kernel eine physikalische Adresse in eine virtuelle Adresse, die im User-Space zur Verfügung steht.

Die GPIO Register werden direkt mit der virtuellen Adresse manipuliert.
Dazu muss eine physikalische Adresse auf einer virtuellen Adresse abgebildet werden.
Dies geschieht mit der folgenden Funktion (**siehe Folien "GPIO with Memory Map", 3 Linux GPIO**): 

```c
virtual_gpio_base = (void *)mmap(
    NULL,
    sysconf(_SC_PAGE_SIZE),
    PROT_READ | PROT_WRITE,
    MAP_SHARED,
    m_mfd,
    GPIO_BASE_ADDR, );
```

Die Kernel Funktion `mmap()` ermöglicht den Zugriff auf eine gesamte Memory-Page des physikalischen Speichers aus einem User-Space-Programm.
Dazu übergibt man der Funktion die physikalische `GPIO_BASE_ADDR` der gewünschten Page als Parameter und erhält eine `virtual_gpio_base` Adresse zurück.

![](./images/mmap.png)

Da die Page Size der MMU 4096 Bytes gross ist, sind die untersten 12 Bit der physkalischen `GPIO_BASE_ADDR`, welche Sie an `mmap()` übergeben werden `0`!

Die Bits 11..0 der _virtuellen_ GPIO Register Adressen sind genau gleich wie die der _physikalischen_ GPIO Register Adressen.
Der `gpio_register_offset` wird somit ohne Umwandlung zur `virtual_gpio_base` Adresse addiert.
Dadurch ergeben sich die virtuellen Adressen der GPIO Register.

```c
virtual_gpio_address = virtual_gpio_base + gpio_register_offset;
```

Um die `virtual_gpio_address` zu finden, benötigen Sie die 35-bit `GPIO_BASE_ADDR`, die dann mit `mmap` in die virtuelle Adresse umgewandelt wird.
Diese Information ist im Device Tree vorhanden (**siehe auch Vorlesung Folien "GPIO with Memory Map", 3 Linux GPIO**):

```
soc {
    compatible = "simple-bus";
    #address-cells = <0x01>;
    #size-cells = <0x01>;
    ranges = <0x7e000000 0x00 0xfe000000 0x1800000
              0x7c000000 0x00 0xfc000000 0x2000000
              0x40000000 0x00 0xff800000 0x800000>;
```
~~~admonish note title="Nice to know: Diese Information selber im Device Tree finden" collapsible=true
Der Device Tree liegt auf der `boot`-Partition der SD-Karte unter `bcm2711-rpi-4-b.dtb`.
Diesen können Sie herunterkopieren, um damit zu arbeiten.
Er ist aber auch auf dem laufenden Raspberry Pi unter `/proc/device-tree` vorhanden.
Sie können beide Quellen verwenden.
Je nachdem, ob der Raspberry Pi gerade läuft oder nicht, ist die eine oder die andere komfortabler.

### Device Tree von der SD-Karte kopiert

Der Device Tree liegt in kompilierter Form vor, wir können ihn so nicht lesen.
(Die Endung`.dtb` steht für "device tree blob".)
_Dekompilieren_ Sie den device tree mit folgendem Befehl:

```sh
dtc -I dtb -O dts -o bcm2711-rpi-4-b.dts bcm2711-rpi-4-b.dtb
```

Dies erzeugt eine neue Datei mit Endung `.dts`, die Sie normal lesen können.
Sie können nun z.B. nach `"soc {"` suchen, um die gewünschte Node zu finden.

### Device Tree von `sysfs` herauslesen

Geben Sie auf dem Target folgenden Befehl ein:

```sh
dtc -I fs -O dts -o ~/rpi.dts /proc/device-tree
```

Auf dem Host finden Sie nun die neue Datei `~/board/rpi.dts`, welche Sie normal lesen können.
Sie können nun z.B. nach `"soc {"` suchen, um die gewünschte Node zu finden.
~~~

## Gerüst



## Adressen und Offsets definieren

Finden Sie die 35-bit ARM View Adresse des `GPIO_BASE_ADDR` heraus und fügen Sie sie in das `#define` im C-Code ein.

Welches sind die Offsets der GPIO Register, welche nach der Umwandlung in eine virtuelle Adresse an die `virtual_gpio_base` Adresse angehängt werden müssen?

(ersichtlich aus dem [BCM2711 Arm Peripherals Manual][datasheet], Chapter 5.2 Register View).

Fügen Sie die gefundenen Adressen der GPIO Offsets wiederum als `#define` im C-Code ein. 

- `GPFSEL0`
- `GPFSEL1`
- `GPSET0`
- `GPCLR0`
- `GPLEV0`

## Implementation

1. Integrieren Sie die Ansteuerung über MMAP wieder in Funktionen, die vom Menu aufgerufen werden können, so dass Sie am Ende alle Möglichkeiten zur Ansteuerung der LED in kurzer Zeit vorführen können.

2. In den Github templates unter gpio finden Sie eine Datei mmap.c und darin die Funktion mmap_virtual_base(). Diese Funktion berechnet aus der GPIO_BASE_ADDR einen globalen Pointer virtual_gpio_base. Hinweis: Damit der Pointer für die nachfolgend beschriebenen Register Steuer-Funktionen, mmap_gpio_direction und mmap_gpio_set, zur Verfügung steht, muss der Pointer im mymenu.c als void *virtual_gpio_base; definiert werden.
Die Funktion `mmap_virtual_base()` wird im `main()` einmal aufgerufen, um den Pointer zu berechnen.
(**Beispiel siehe Folien "GPIO with Memory Map", "3 Linux GPIO"**)

3. Implementieren Sie die Funktion `mmap_gpio_direction()` zum Setzen der Richtung der GPIO-Pins wie zu Beginn der Folien **"3 Linux GPIO"** beschrieben.
Der Funktion wird der GPIO-Pin und die Direction als Integer übergeben.
"Direction = 1" bedeutet Output, " Direction = 0" bedeutet Input.
Die Funktion manipuliert die Bits des entsprechende GPIO-FSELx Registers mithilfe eines Pointers `gpio_reg`.

4. Erstellen Sie eine Funktion void mmap_gpio_set() zum Setzen oder Löschen einzelner GPIO-Pins wie zu Beginn der Folien "3 Linux GPIO", beschrieben.
Der Funktion void mmap_gpio_set(int gpio, int value) wird der GPIO-Pin  und der Value als Integer übergeben. "Value= 1" bedeutet High-Level," Value= 0" bedeutet Low-Level.
Die LEDs (4 und 5) an GPIO12 und 13 sind so angeschlossen, dass sie bei High-Level leuchten (Achtung: andere GPIOs, z.B. die der 7-Segment Anzeige sind Low-Aktiv angeschlossen)
Die Funktion manipuliert die Bits der entsprechende GPIO-Set und GPIO-CLR Register mithilfe eines Pointers gpio_reg (siehe Template File mmap.c).

5. Bauen Sie jetzt in das Menu-Interface von `mymenu.c` die Funktionen zum Setzen der GPIO Direction und zum Setzen und Löschen der GPIO Values ein.
Rufen Sie von dort die Funktionen `mmap_gpio_direction()` und `mmap_gpio_set()` auf.

6. Testen Sie die Funktionen aus und setzen Sie LEDs 4 und 5 unabhängig voneinander.
Halten Sie `mymenu.c` bereit, um es der Praktikumsbetreuum am Ende der Laborübung vorzuführen.

[datasheet]: https://datasheets.raspberrypi.com/bcm2711/bcm2711-peripherals.pdf
