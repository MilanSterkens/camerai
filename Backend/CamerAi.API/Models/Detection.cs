using CamerAi.DAL.DTOs;

namespace CamerAi.API.Models;

public sealed class Detection
{
    public double Speed { get; set; }
    public double? MaxSpeed { get; set; }
    public VehicleType Type { get; set; }
    public DateTime Time { get; set; }
    public double? Latitude { get; set; }
    public double? Longitude { get; set; }
}