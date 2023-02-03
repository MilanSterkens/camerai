using CamerAi.DAL.DTOs;

namespace CamerAi.API.Models;

public sealed class VehicleDeviceMaxSpeed
{
    public int Id { get; set; }
    public VehicleType Type { get; set; }
    public string DeviceUniqueId { get; set; }
    public int MaxSpeed { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
}