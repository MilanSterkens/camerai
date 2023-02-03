using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CamerAi.API.Migrations
{
    public partial class maxspeed : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "DeviceId",
                table: "VehicleDeviceMaxSpeeds");

            migrationBuilder.AddColumn<string>(
                name: "DeviceUniqueId",
                table: "VehicleDeviceMaxSpeeds",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "DeviceUniqueId",
                table: "VehicleDeviceMaxSpeeds");

            migrationBuilder.AddColumn<int>(
                name: "DeviceId",
                table: "VehicleDeviceMaxSpeeds",
                type: "int",
                nullable: false,
                defaultValue: 0);
        }
    }
}
