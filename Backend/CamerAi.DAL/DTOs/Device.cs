namespace CamerAi.DAL.DTOs;

public sealed class Device : Entity
{
    public string UniqueId { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public ICollection<VehicleDetection>? Detections { get; set; }
}