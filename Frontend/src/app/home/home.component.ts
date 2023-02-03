import {Component, OnInit} from '@angular/core';
import {CameraiService} from "../service/camerai.service";
import {circle, latLng, tileLayer} from "leaflet";
import 'leaflet'
import {Router} from "@angular/router";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  toggle: boolean = true;
  toggleLocation: boolean = true;
  devices: any[] = [];
  selectedDevice: any;
  maxSpeedCar: number = 0;
  maxSpeedBus: number = 0;
  maxSpeedBike: number = 0;
  maxSpeedMotorcycle: number = 0;
  // maxSpeeds: [] = [];
  options: any = {
    layers: [],
    zoom: 8,
    center: latLng([0, 0]),
  };
  locationsMaxSpeed: any[] = [];
  latLong: any[] = [];
  selectedLat: any;
  selectedLong: any;
  isLastLocation: boolean = false;

  constructor(private service: CameraiService) {
    this.service.getDevices().subscribe((devices) => {
      this.devices = devices;
    });
    this.selectedDevice = this.devices[0];
    this.options.layers = [];
  }

  ngOnInit(): void {
    this.options.layers = [];
    this.selectedDevice = this.devices[0];
    this.options = {
      layers: [
        tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
      ],
      zoom: 8,
      center: latLng(this.selectedLat, this.selectedLong)
    };
  }

  toggleDropdown() {
    this.toggle = !this.toggle;
  }

  toggleDropdownLocation() {
    this.toggleLocation = !this.toggleLocation;
  }

  clickDevice(id: number) {
    this.selectedLong = 0;
    this.selectedLat = 0;
    this.latLong = [];

    this.selectedDevice = this.devices.find(device => device.id === id);

    this.service.getDevice(this.selectedDevice.uniqueId).subscribe((locations) => {
      this.locationsMaxSpeed = locations;
      this.locationsMaxSpeed.forEach((item) => {
        let obj = {
          latitude: item.latitude,
          longitude: item.longitude
        };

        if (this.latLong.some((el) => el.latitude == obj.latitude && el.longitude == obj.longitude)) {
          return;
        }
        this.latLong.push(obj);
      });

    });
    this.toggleDropdown();
  }

  clickLocation(lat: number, long: number) {
    this.selectedLat = lat;
    this.selectedLong = long;

    const lastObject = this.latLong[this.latLong.length - 1];

    this.isLastLocation = this.selectedLat === lastObject.latitude && this.selectedLong === lastObject.longitude;

    this.options.center = latLng(this.selectedLat, this.selectedLong);
    this.options.layers = [
      tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
      circle([this.selectedLat, this.selectedLong], {radius: 5000}),
    ];

    this.service.getMaxSpeed(this.selectedDevice.uniqueId, long, lat).subscribe((speeds) => {
      if (speeds.length > 1) {
        let maxSpeedCar = speeds.find(speed => speed.type === 1);
        if (maxSpeedCar) this.maxSpeedCar = maxSpeedCar.maxSpeed;
        let maxSpeedBus = speeds.find(speed => speed.type === 2);
        if (maxSpeedBus) this.maxSpeedBus = maxSpeedBus.maxSpeed;
        let maxSpeedBike = speeds.find(speed => speed.type === 3);
        if (maxSpeedBike) this.maxSpeedBike = maxSpeedBike.maxSpeed;
        let maxSpeedMotor = speeds.find(speed => speed.type === 4);
        if (maxSpeedMotor) this.maxSpeedMotorcycle = maxSpeedMotor.maxSpeed;
      } else {
        this.maxSpeedCar = 0;
        this.maxSpeedBus = 0;
        this.maxSpeedBike = 0;
        this.maxSpeedMotorcycle = 0;
      }
    });
    this.toggleDropdownLocation();
  }

  submitMaxSpeed() {
    this.service.postMaxSpeed(1, this.maxSpeedCar, this.selectedDevice.uniqueId, this.selectedLong, this.selectedLat).subscribe((any) => {
    });
    this.service.postMaxSpeed(2, this.maxSpeedBus, this.selectedDevice.uniqueId, this.selectedLong, this.selectedLat).subscribe((any) => {
    });
    this.service.postMaxSpeed(3, this.maxSpeedBike, this.selectedDevice.uniqueId, this.selectedLong, this.selectedLat).subscribe((any) => {
    });
    this.service.postMaxSpeed(4, this.maxSpeedMotorcycle, this.selectedDevice.uniqueId, this.selectedLong, this.selectedLat).subscribe((any) => {
    });
  }
}
